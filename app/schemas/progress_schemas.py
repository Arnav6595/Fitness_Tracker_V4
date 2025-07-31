# app/schemas/progress_schemas.py
from pydantic import BaseModel, Field
from typing import Optional

class WeightLogSchema(BaseModel):
    user_id: int
    weight_kg: float = Field(gt=0, description="Weight must be a positive number.")
    date: Optional[str] = None

class MeasurementLogSchema(BaseModel):
    user_id: int
    date: Optional[str] = None
    waist_cm: Optional[float] = Field(None, gt=0)
    chest_cm: Optional[float] = Field(None, gt=0)
    arms_cm: Optional[float] = Field(None, gt=0)
    hips_cm: Optional[float] = Field(None, gt=0)