# app/schemas/diet_schemas.py
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Literal
from datetime import datetime

class MacroSchema(BaseModel):
    protein_g: Optional[float] = Field(None, ge=0)
    carbs_g: Optional[float] = Field(None, ge=0)
    fat_g: Optional[float] = Field(None, ge=0)

class DietLogSchema(BaseModel):
    user_id: int
    meal_name: str = Field(..., min_length=2) # ... means the field is required
    calories: int = Field(..., gt=0)
    food_items: Optional[str] = None
    macros: Optional[MacroSchema] = None
    date: Optional[str] = None

    @field_validator('date')
    def validate_date_format(cls, value):
        if value is None:
            return value
        try:
            datetime.fromisoformat(value)
        except ValueError:
            raise ValueError("Incorrect date format, should be YYYY-MM-DDTHH:MM:SS")
        return value

class GenerateDietPlanSchema(BaseModel):
    user_id: int
    activityLevel: Literal['sedentary', 'lightlyActive', 'moderatelyActive', 'veryActive', 'extraActive']
    diet_type: Literal['veg', 'non-veg']
    budget: Optional[str] = None
    optional_cuisines: Optional[List[str]] = None