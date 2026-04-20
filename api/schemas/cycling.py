from pydantic import BaseModel, Field
from typing import Optional, Literal

class CyclingInputSimple(BaseModel):
    mode: Literal["simple"] = "simple"
    age: int = Field(..., ge=15, le=85)
    gender: int = Field(..., ge=0, le=1, description="0=homme, 1=femme")

class CyclingInputAdvanced(BaseModel):
    mode: Literal["advanced"] = "advanced"
    age: int = Field(..., ge=15, le=85)
    gender: int = Field(..., ge=0, le=1)
    ref_distance_km: float = Field(..., ge=5, le=200, description="Distance de référence en km")
    ref_time_seconds: int = Field(..., ge=600, le=36000, description="Temps sur la distance de référence (secondes)")

class DistancePredictionCycling(BaseModel):
    distance: str
    seconds: int
    formatted: str
    speed_kmh: float

class CyclingOutput(BaseModel):
    sport: str = "cycling"
    mode: str
    level_label: str
    predictions: list[DistancePredictionCycling]
    method: str
    confidence: Literal["low", "medium", "high"]
    disclaimer: Optional[str]
