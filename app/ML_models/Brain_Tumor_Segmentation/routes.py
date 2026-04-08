import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

from cv2.gapi import mask
from fastapi import APIRouter, UploadFile, File, HTTPException, Response
import numpy as np
import cv2

from app.ML_models.Brain_Tumor_Segmentation.utils import validate_file_extension, validate_file_content, validate_image_content, preprocess_image
from app.ML_models.Brain_Tumor_Segmentation.utils import get_model

model = get_model()
segmentation_router = APIRouter()


@segmentation_router.post("/predict")
async def upload_file(file: UploadFile = File(...)):
    
    # Step 0: validate file and extract contents
    validate_file_extension(str(file.filename))
    contents = await validate_file_content(file)

    # Step 1: decode
    img = validate_image_content(contents)

    # Step 2: save original BEFORE preprocessing
    img_original = img.copy()

    # Step 3: preprocess for model
    img = preprocess_image(img)

    # Step 4: prepare original for display
    img_original = cv2.cvtColor(img_original, cv2.COLOR_BGR2RGB)
    img_original = cv2.resize(img_original, (256, 256))

    # Step 5: predict
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

    return Response(content=encoded_img.tobytes(), media_type="image/png")