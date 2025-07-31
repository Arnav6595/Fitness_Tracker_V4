from pydantic import BaseModel, Field, field_validator, EmailStr
from typing import Optional, Literal
from datetime import datetime

class MembershipSchema(BaseModel):
    plan: str = Field(min_length=3, max_length=50)
    end_date: Optional[str] = None

    # Custom validator to ensure the date string is in the correct format
    @field_validator('end_date')
    def validate_date_format(cls, value):
        if value is None:
            return value
        try:
            datetime.strptime(value, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Incorrect date format, should be YYYY-MM-DD")
        return value

class UserRegistrationSchema(BaseModel):
    # Required Fields with Validation
    name: str = Field(min_length=2, max_length=100, description="User's full name")
    age: int = Field(gt=13, lt=100, description="User's age, must be between 14 and 99")
    gender: Literal['Male', 'Female', 'Other']
    contact_info: EmailStr # Pydantic will automatically validate this is a valid email format
    weight_kg: float = Field(gt=20, description="Weight in kilograms, must be greater than 20")
    height_cm: float = Field(gt=100, description="Height in centimeters, must be greater than 100")
    fitness_goals: str = Field(min_length=5, max_length=200)
    workouts_per_week: str
    workout_duration: int = Field(gt=0)
    sleep_hours: str
    stress_level: Literal['low', 'medium', 'high']
    
    # Nested Schema for Membership
    membership: Optional[MembershipSchema] = None

    # Optional Fields (can be omitted from the request)
    disliked_foods: Optional[str] = None
    allergies: Optional[str] = None
    health_conditions: Optional[str] = None

    # Pydantic configuration example
    class ConfigDict:
        str_strip_whitespace = True
        validate_assignment = True
        extra = 'forbid' # Forbid any extra fields not defined in the schema