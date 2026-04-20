from pydantic import BaseModel, Field, model_validator
from typing import Optional, Literal
from enum import IntEnum

class Gender(IntEnum):
    male = 0
    female = 1

class RunningInputSimple(BaseModel):
    mode: Literal["simple"] = "simple"
    age: int = Field(..., ge=15, le=85, description="Âge en années")
    gender: Gender = Field(..., description="0=homme, 1=femme")
    resting_hr: int = Field(..., ge=30, le=100, description="FC repos (bpm)")
    max_hr: Optional[int] = Field(None, ge=120, le=220, description="FC max (bpm)")
    weight_kg: Optional[float] = Field(None, ge=30, le=150, description="Poids (kg)")

class RunningInputAdvanced(BaseModel):
    mode: Literal["advanced"] = "advanced"
    age: int = Field(..., ge=15, le=85)
    gender: Gender
    recent_5k_seconds: Optional[int] = Field(None, ge=600, le=7200, description="Temps 5K récent (secondes)")
    recent_10k_seconds: Optional[int] = Field(None, ge=1200, le=14400, description="Temps 10K récent (secondes)")

    @model_validator(mode="after")
    def check_at_least_one_time(self):
        if self.recent_5k_seconds is None and self.recent_10k_seconds is None:
            raise ValueError("Au moins un temps de référence (5K ou 10K) est requis en mode avancé.")
        return self

class DistancePrediction(BaseModel):
    distance: str
    seconds: int
    formatted: str

class RunningOutput(BaseModel):
    sport: str = "running"
    mode: str
    level_label: str
    predictions: list[DistancePrediction]
    vo2max_estimated: Optional[float]
    method: str
    confidence: Literal["low", "medium", "high"]
    disclaimer: Optional[str]
