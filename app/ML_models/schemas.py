from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


# __________________Schemas for ML Models________________________________________________________________________________________________
class ModelBase(BaseModel):
    model_name: str = Field(..., example="unet_brain_seg")
    version: str = Field(..., example="v1")
    description: Optional[str] = Field(None, example="UNet trained on BraTS dataset")
    framework: str = Field(..., example="pytorch")
    model_type: str = Field(..., example="segmentation")
    model_path: str = Field(..., example="models/unet_v1.pth")
    metrics : Optional[dict] = Field(None, example={"dice_score": 0.85, "iou": 0.80})

class ModelCreate(ModelBase):
    added_by : UUID = Field(..., example="123e4567-e89b-12d3-a456-426614174000")


class ModelResponse(ModelBase):
    id : UUID
    created_at : datetime
    added_by : UUID



# __________________Schemas for Predictions________________________________________________________________________________________________
class PredictionCreate(BaseModel):
    prediction_id : UUID
    user_id  : UUID 
    model_id : UUID 
    input_path : str
    mask_path : str
    inference_time : float