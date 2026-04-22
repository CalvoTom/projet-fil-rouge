from pydantic import BaseModel, Field
from typing import Optional, Literal


class TennisInputSimple(BaseModel):
    mode: Literal["simple"] = "simple"
    age: int = Field(..., ge=10, le=60)
    gender: int = Field(..., ge=0, le=1, description="0=homme, 1=femme")
    height_cm: float = Field(..., ge=140, le=220, description="Taille en cm")
    years_practice: float = Field(..., ge=0, le=40,
                                   description="Années de pratique du tennis")


class TennisInputAdvanced(BaseModel):
    mode: Literal["advanced"] = "advanced"
    gender: int = Field(..., ge=0, le=1, description="0=homme, 1=femme")
    first_serve_pct: float = Field(..., ge=0, le=100,
                                    description="% de 1ères balles entrées")
    ace_rate: float = Field(..., ge=0, le=30,
                             description="% d'aces par point de service")
    df_rate: float = Field(..., ge=0, le=30,
                            description="% de doubles fautes par point de service")
    first_serve_won_pct: float = Field(..., ge=0, le=100,
                                        description="% de points gagnés sur 1ère balle")
    second_serve_won_pct: float = Field(..., ge=0, le=100,
                                         description="% de points gagnés sur 2ème balle")
    bp_saved_pct: float = Field(50.0, ge=0, le=100,
                                 description="% de balles de break sauvées (optionnel)")


class TennisOutput(BaseModel):
    sport: str = "tennis"
    mode: str
    level_class: int
    level_label: str
    level_equiv: str
    level_rank_range: str
    confidence: Literal["low", "medium", "high"]
    probabilities: Optional[dict]
    ref_stats: Optional[dict]
    method: str
    disclaimer: Optional[str]
