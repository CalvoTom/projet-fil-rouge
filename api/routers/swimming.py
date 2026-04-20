from fastapi import APIRouter
from api.schemas.swimming import SwimmingInputSimple, SwimmingInputAdvanced, SwimmingOutput
from api.services import swimming_service

router = APIRouter(prefix="/swimming", tags=["Swimming"])

@router.post("/predict/simple", response_model=SwimmingOutput)
def predict_swimming_simple(data: SwimmingInputSimple):
    result = swimming_service.predict_simple(age=data.age, gender=data.gender)
    return SwimmingOutput(**result)

@router.post("/predict/advanced", response_model=SwimmingOutput)
def predict_swimming_advanced(data: SwimmingInputAdvanced):
    result = swimming_service.predict_advanced(
        age=data.age,
        gender=data.gender,
        ref_distance_m=data.ref_distance_m,
        ref_time_seconds=data.ref_time_seconds,
    )
    return SwimmingOutput(**result)
