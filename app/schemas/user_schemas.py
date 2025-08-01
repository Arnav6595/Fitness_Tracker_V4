# app/schemas/user_schemas.py

from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional, Literal
from datetime import datetime

class MembershipSchema(BaseModel):
    """
    Defines the structure for membership information provided during registration.
    """
    plan: str = Field(min_length=3, max_length=50)

class UserRegistrationSchema(BaseModel):
    """
    Validates the incoming data for the user registration endpoint.
    """
    # --- Authentication Fields ---
    email: EmailStr  # Changed from contact_info
    password: str = Field(min_length=8, description="User's password must be at least 8 characters.")
    phone_number: Optional[str] = None # Added new optional field

    # --- User Profile Fields ---
    name: str = Field(min_length=2, max_length=100, description="User's full name")
    age: int = Field(gt=13, lt=100, description="User's age, must be between 14 and 99")
    gender: Literal['Male', 'Female', 'Other']
    weight_kg: float = Field(gt=20, description="Weight in kilograms, must be greater than 20")
    height_cm: float = Field(gt=100, description="Height in centimeters, must be greater than 100")
    fitness_goals: str = Field(min_length=5, max_length=200)
    workouts_per_week: str
    workout_duration: int = Field(gt=0, description="Duration in minutes.")
    sleep_hours: str
    stress_level: Literal['low', 'medium', 'high']
    
    # --- Optional Fields ---
    disliked_foods: Optional[str] = None
    allergies: Optional[str] = None
    health_conditions: Optional[str] = None

    # --- Nested Schema ---
    membership: Optional[MembershipSchema] = None

    class Config:
        # Pydantic v1 style config for compatibility, can be ConfigDict in v2
        str_strip_whitespace = True

class UserLoginSchema(BaseModel):
    """
    Validates the incoming data for the user login endpoint.
    """
    email: EmailStr
    password: str