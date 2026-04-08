import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

from fastapi import APIRouter, UploadFile, File, HTTPException, Response
import numpy as np
import cv2
import uuid
from pathlib import Path

from app.ML_models.Brain_Tumor_Segmentation.utils import validate_file_extension, validate_file_content, validate_image_content, preprocess_image
from app.ML_models.Brain_Tumor_Segmentation.utils import get_model


# Model and other dependencies
model = get_model()
segmentation_router = APIRouter()


# Storage dependencies
BASE_DIR = Path("segmentation_storage")
INPUT_DIR = BASE_DIR / "input"
MASK_DIR = BASE_DIR / "mask"

INPUT_DIR.mkdir(parents=True, exist_ok=True)
MASK_DIR.mkdir(parents=True, exist_ok=True)



@segmentation_router.post("/predict",description="Upload an image for brain tumor segmentation. Supported formats: .tif, .tiff, .png")
async def upload_file(file: UploadFile = File(...)):
    prediction_id_db = uuid.uuid4()
    prediction_id = str(prediction_id_db)

    # Step 0: validate file and extract contents
    validate_file_extension(str(file.filename))
    contents = await validate_file_content(file)

    # Step 1: decode
    img = validate_image_content(contents)

    # Step 2: save original BEFORE preprocessing
    img_original = img.copy()
    img_to_save = img.copy()

    # Step 3: preprocess for model
    img = preprocess_image(img)

    # Step 4: prepare original for display
    img_original = cv2.cvtColor(img_original, cv2.COLOR_BGR2RGB)
    img_original = cv2.resize(img_original, (256, 256))

    # Step 5: prediction
    img = np.expand_dims(img, axis=0)
    predicted_mask = model.predict(img)
    mask = (predicted_mask > 0.5).astype(np.uint8)
    mask = np.squeeze(mask)

    # Step 6: overlay
    overlay = img_original.copy()
    alpha = 0.55
    overlay[mask == 1] = (alpha * np.array([255, 0, 0]) + (1 - alpha) * overlay[mask == 1]).astype(np.uint8)

    # Step 7: convert to BGR for encoding
    overlay = cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR)

    # Step 8: encode
    success, encoded_img = cv2.imencode(".png", overlay)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to encode image")

    # Step 9 : Save images
    input_to_save = cv2.cvtColor(img_to_save, cv2.COLOR_RGB2BGR)
    mask_to_save = (mask * 255).astype(np.uint8)

    input_path = INPUT_DIR / f"input_{prediction_id}.png"
    mask_path = MASK_DIR / f"mask_{prediction_id}.png"

    if not cv2.imwrite(str(input_path), input_to_save):
        raise HTTPException(status_code=500, detail="Failed to save input image")
    if not cv2.imwrite(str(mask_path), mask_to_save):
        raise HTTPException(status_code=500, detail="Failed to save mask image")


    # Step 10: return response
    return Response(content=encoded_img.tobytes(), media_type="image/png",headers={"X-Prediction-ID": prediction_id})