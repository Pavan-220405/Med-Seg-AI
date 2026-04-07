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




# ── Quick smoke-test ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    init_model()
    model.summary()