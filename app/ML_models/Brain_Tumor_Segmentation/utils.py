from typing import Optional
from pathlib import Path

import tensorflow as tf
from tensorflow import keras
from keras import backend as K

# ── Model state ───────────────────────────────────────────────────────────────
model: Optional[keras.Model] = None
model_path = Path(__file__).parent / "best_model.h5"


# ── Custom metric / loss functions ────────────────────────────────────────────
def dice_coef(y_true, y_pred, smooth: float = 1.0):
    y_true_f = K.flatten(y_true)
    y_pred_f = K.flatten(y_pred)
    intersection = K.sum(y_true_f * y_pred_f)
    return (2.0 * intersection + smooth) / (K.sum(y_true_f) + K.sum(y_pred_f) + smooth)


def dice_loss(y_true, y_pred, smooth: float = 1.0):
    return 1.0 - dice_coef(y_true, y_pred, smooth)


def iou_coef(y_true, y_pred, smooth: float = 1.0):
    y_true_f = K.flatten(y_true)
    y_pred_f = K.flatten(y_pred)
    intersection = K.sum(y_true_f * y_pred_f)
    union = K.sum(y_true_f + y_pred_f)
    return (intersection + smooth) / (union - intersection + smooth)


_CUSTOM_OBJECTS = {
    "dice_coef": dice_coef,
    "iou_coef":  iou_coef,
    "dice_loss": dice_loss,
}


# ── Lifecycle helpers (called by FastAPI lifespan) ────────────────────────────
def init_model() -> None:
    global model
    model = tf.keras.models.load_model(
        model_path,
        custom_objects=_CUSTOM_OBJECTS,
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


# ── Quick smoke-test ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    init_model()
    model.summary()