from fastapi import APIRouter
from api.schemas.cycling import CyclingInputSimple, CyclingInputAdvanced, CyclingOutput
from api.services import cycling_service

router = APIRouter(prefix="/cycling", tags=["Cycling"])

@router.post("/predict/simple", response_model=CyclingOutput)
def predict_cycling_simple(data: CyclingInputSimple):
    result = cycling_service.predict_simple(age=data.age, gender=data.gender)
    return CyclingOutput(**result)

@router.post("/predict/advanced", response_model=CyclingOutput)
def predict_cycling_advanced(data: CyclingInputAdvanced):
    result = cycling_service.predict_advanced(
        age=data.age,
        gender=data.gender,
        ref_distance_km=data.ref_distance_km,
        ref_time_seconds=data.ref_time_seconds,
    )
    return CyclingOutput(**result)
