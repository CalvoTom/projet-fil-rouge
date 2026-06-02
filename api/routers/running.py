from fastapi import APIRouter, HTTPException
from api.schemas.running import RunningInputSimple, RunningInputAdvanced, RunningOutput
from api.services import running_service

router = APIRouter(prefix="/running", tags=["Running"])

@router.post("/predict/simple", response_model=RunningOutput)
def predict_running_simple(data: RunningInputSimple):
    try:
        result = running_service.predict_simple(
            age=data.age,
            gender=int(data.gender),
            resting_hr=data.resting_hr,
            max_hr=data.max_hr,
            weight_kg=data.weight_kg,
        )
        return RunningOutput(**result)
    except FileNotFoundError:
        raise HTTPException(status_code=503, detail="Modèle introuvable. Relancez retrain_models.py.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/predict/advanced", response_model=RunningOutput)
def predict_running_advanced(data: RunningInputAdvanced):
    try:
        result = running_service.predict_advanced(
            age=data.age,
            gender=int(data.gender),
            recent_5k_seconds=data.recent_5k_seconds,
            recent_10k_seconds=data.recent_10k_seconds,
        )
        return RunningOutput(**result)
    except FileNotFoundError:
        raise HTTPException(status_code=503, detail="Modèle introuvable. Relancez retrain_models.py.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
