from typing import Optional
from pathlib import Path

import tensorflow as tf
from tensorflow import keras
from keras import backend as K

# ── Model state ───────────────────────────────────────────────────────────────
model: Optional[keras.Model] = None
model_path = Path(__file__).parent / "best_model.h5"


# ── Lifecycle helpers (called by FastAPI lifespan) ────────────────────────────
def init_model() -> None:
    global model
    model = tf.keras.models.load_model(
        model_path,
        compile=False
    )
    print("✅ Brain-Tumor Segmentation model loaded successfully.")


def get_model() -> keras.Model:
    if model is None:
        init_model()
    return model


def close_model() -> None:
    global model
    if model is not None:
        del model
        model = None
        print("🛑 Model unloaded.")




# ── Utility functions for file validation and image preprocessing ────────────────────────────
from fastapi import HTTPException, UploadFile
import numpy as np
import cv2


allowed_extensions = {'.tif', '.tiff' ,'.png'}


def validate_file_extension(filename : str):
    if not filename:
        raise HTTPException(status_code=400, detail="No file uploaded.")

    ext = "." + filename.split(".")[-1].lower()
    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Unsupported file type. Only {allowed_extensions} are allowed.")
    return True



async def validate_file_content(file : UploadFile):
    try:
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")
        return contents
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")
    


def validate_image_content(contents: bytes):
    try:
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
        if img is None:
            raise HTTPException(status_code=400, detail="Uploaded file is not a valid image.")
        return img
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")
    


def preprocess_image(img):
    try:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (256, 256))
        img = img.astype(np.float32) / 255.0
        return img
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error preprocessing image: {str(e)}")