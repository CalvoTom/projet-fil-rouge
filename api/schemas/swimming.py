from pydantic import BaseModel, Field
from typing import Optional, Literal

class SwimmingInputSimple(BaseModel):
    mode: Literal["simple"] = "simple"
    age: int = Field(..., ge=10, le=85)
    gender: int = Field(..., ge=0, le=1, description="0=homme, 1=femme")

class SwimmingInputAdvanced(BaseModel):
    mode: Literal["advanced"] = "advanced"
    age: int = Field(..., ge=10, le=85)
    gender: int = Field(..., ge=0, le=1)
    ref_distance_m: int = Field(..., ge=100, le=5000, description="Distance de référence en mètres")
    ref_time_seconds: int = Field(..., ge=40, le=7200, description="Temps sur la distance de référence (secondes)")

class DistancePredictionSwimming(BaseModel):
    distance: str
    seconds: int
    formatted: str
    pace_per_100m: str

class SwimmingOutput(BaseModel):
    sport: str = "swimming"
    mode: str
    level_label: str
    predictions: list[DistancePredictionSwimming]
    method: str
    confidence: Literal["low", "medium", "high"]
    disclaimer: Optional[str]
