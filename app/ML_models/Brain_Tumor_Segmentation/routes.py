from fastapi import APIRouter, File, UploadFile, HTTPException
import cv2
import numpy as np
import base64
import tifffile as tiff
import io

from app.ML_models.Brain_Tumor_Segmentation.utils import get_model


model = get_model()
segmentation_router = APIRouter()


@segmentation_router.post('/predict_tumor')
async def predict_tumor(file: UploadFile = File(...)):

    if file.content_type not in {
        'image/tiff', 'image/tif', 'image/jpeg', 'image/png'
    }:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Use TIFF, JPEG, or PNG."
        )

    contents = await file.read()

    # =========================
    # 🔹 TIFF Handling (FIXED)
    # =========================
    if file.content_type in {'image/tiff', 'image/tif'}:
        try:
            image = tiff.imread(io.BytesIO(contents))  # ✅ FIX HERE
        except Exception as e:
            raise HTTPException(400, f"TIFF read error: {str(e)}")

        # Multi-slice (3D MRI)
        if len(image.shape) == 3:
            image = image[image.shape[0] // 2]

        # Grayscale → RGB
        if len(image.shape) == 2:
            image = np.stack([image] * 3, axis=-1)

        # Normalize (handles 16-bit)
        image = image.astype(np.float32)
        image = (image - image.min()) / (image.max() - image.min() + 1e-8)

    # =========================
    # 🔹 JPEG / PNG Handling
    # =========================
    else:
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if image is None:
            raise HTTPException(400, "Invalid image file")

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = image.astype(np.float32) / 255.0

    # =========================
    # 🔹 Resize + Model Input
    # =========================
    image_resized = cv2.resize(image, (256, 256))
    img_input = image_resized[np.newaxis, :, :, :]

    # =========================
    # 🔹 Prediction
    # =========================
    predicted_img = model.predict(img_input)

    # =========================
    # 🔹 Create Mask
    # =========================
    mask = (predicted_img[0, :, :, 0] > 0.5).astype(np.uint8) * 255

    # =========================
    # 🔹 Convert images to PNG
    # =========================
    original_uint8 = (image_resized * 255).astype(np.uint8)

    _, orig_buffer = cv2.imencode(".png", original_uint8)
    _, mask_buffer = cv2.imencode(".png", mask)

    # =========================
    # 🔹 Base64 Encode
    # =========================
    orig_base64 = base64.b64encode(orig_buffer).decode("utf-8")
    mask_base64 = base64.b64encode(mask_buffer).decode("utf-8")

    # =========================
    # 🔹 Response
    # =========================
    return {
        "tumor_detected": bool(mask.sum() > 0),
        "original_image": orig_base64,
        "predicted_mask": mask_base64
    }