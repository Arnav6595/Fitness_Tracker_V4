# app/schemas/workout_schemas.py
from pydantic import BaseModel, Field
from typing import Optional, List, Literal

# Schema for a single exercise entry within a workout log
class ExerciseSchema(BaseModel):
    name: str = Field(min_length=2)
    sets: int = Field(gt=0)
    reps: int = Field(gt=0)
    weight: float = Field(ge=0) # Greater than or equal to 0 for bodyweight

# Schema for the entire workout log request
class WorkoutLogSchema(BaseModel):
    #user_id: int
    name: str = Field(min_length=3)
    date: Optional[str] = None
    exercises: List[ExerciseSchema] = Field(min_length=1)

# Schema for the workout plan generation request
class GenerateWorkoutPlanSchema(BaseModel):
    user_id: int
    fitnessLevel: Literal['beginner', 'intermediate', 'advanced']
    equipment: Literal['bodyweight only', 'Home gym', 'Gym access']