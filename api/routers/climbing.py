from fastapi import APIRouter
from api.schemas.climbing import ClimbingInput, ClimbingOutput
from api.services import climbing_service

router = APIRouter(prefix="/climbing", tags=["Escalade"])

@router.post("/predict", response_model=ClimbingOutput)
def predict_climbing(data: ClimbingInput):
    result = climbing_service.predict(
        gender=int(data.gender),
        height_cm=data.height_cm,
        weight_kg=data.weight_kg,
        age=data.age,
        years_climbing=data.years_climbing,
        dead_hang_seconds=data.dead_hang_seconds,
        max_pullups=data.max_pullups,
    )
    return ClimbingOutput(**result)
