from fastapi import APIRouter
from api.schemas.tennis import TennisInputSimple, TennisInputAdvanced, TennisOutput
from api.services import tennis_service

router = APIRouter(prefix="/tennis", tags=["Tennis"])


@router.post("/predict/simple", response_model=TennisOutput)
def predict_tennis_simple(data: TennisInputSimple):
    result = tennis_service.predict_simple(
        age=data.age,
        gender=data.gender,
        height_cm=data.height_cm,
        years_practice=data.years_practice,
    )
    return TennisOutput(**result)


@router.post("/predict/advanced", response_model=TennisOutput)
def predict_tennis_advanced(data: TennisInputAdvanced):
    result = tennis_service.predict_advanced(
        gender=data.gender,
        first_serve_pct=data.first_serve_pct,
        ace_rate=data.ace_rate,
        df_rate=data.df_rate,
        first_serve_won_pct=data.first_serve_won_pct,
        second_serve_won_pct=data.second_serve_won_pct,
        bp_saved_pct=data.bp_saved_pct,
    )
    return TennisOutput(**result)
