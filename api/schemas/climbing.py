from pydantic import BaseModel, Field
from typing import Optional, Literal
from enum import IntEnum

class Gender(IntEnum):
    male = 0
    female = 1

class ClimbingInput(BaseModel):
    age: int = Field(..., ge=10, le=80)
    gender: Gender
    height_cm: float = Field(..., ge=140, le=220)
    weight_kg: float = Field(..., ge=40, le=130)
    years_climbing: float = Field(..., ge=0, le=50, description="Années de pratique (0 = jamais grimpé)")
    dead_hang_seconds: Optional[int] = Field(None, ge=0, le=300, description="Temps suspension barre (secondes)")
    max_pullups: Optional[int] = Field(None, ge=0, le=50, description="Nombre max de tractions")

class ClimbingOutput(BaseModel):
    sport: str = "climbing"
    mode_used: Literal["potential", "ml"]
    level_class: int
    level_label: str
    grade_range: str
    confidence: Literal["low", "medium", "high"]
    probabilities: Optional[dict[str, float]]
    disclaimer: Optional[str]
