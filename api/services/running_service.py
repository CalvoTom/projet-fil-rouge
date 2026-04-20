import joblib
import numpy as np
import pandas as pd
from pathlib import Path

MODEL_PATH = Path(__file__).parent.parent.parent / "models" / "running_model.pkl"
_model = None

def _load_model():
    global _model
    if _model is None:
        _model = joblib.load(MODEL_PATH)
    return _model

def _seconds_to_formatted(s: int) -> str:
    s = int(s)
    h = s // 3600
    m = (s % 3600) // 60
    sec = s % 60
    if h > 0:
        return f"{h}h{m:02d}m{sec:02d}s"
    return f"{m}m{sec:02d}s"

def _riegel(t1_sec: float, d1_km: float, d2_km: float) -> int:
    return int(t1_sec * (d2_km / d1_km) ** 1.06)

def _estimate_vo2max_from_hr(resting_hr: int, max_hr: int = None, age: int = None) -> float:
    """Estimation VO2max depuis FC repos (formule simplifiée de Uth et al.)."""
    if max_hr is None:
        max_hr = 220 - age
    return 15.3 * (max_hr / resting_hr)

def _vdot_to_marathon(vo2max: float, gender: int) -> int:
    """
    Approximation du temps marathon depuis VO2max via tables Jack Daniels.
    Correction de genre appliquée.
    """
    # Formule empirique inverse de la table VDOT (approximation polynomiale)
    # VO2max → vitesse marathon (km/h)
    speed_kmh = 0.1607 * vo2max - 0.3435
    speed_kmh = max(4.0, min(speed_kmh, 22.0))
    if gender == 1:  # femme
        speed_kmh *= 0.90
    marathon_sec = int((42.195 / speed_kmh) * 3600)
    return marathon_sec

DISTANCES = [
    ("5km", 5.0),
    ("10km", 10.0),
    ("Semi-marathon", 21.0975),
    ("Marathon", 42.195),
]

def predict_simple(age: int, gender: int, resting_hr: int,
                   max_hr: int = None, weight_kg: float = None):
    vo2max = _estimate_vo2max_from_hr(resting_hr, max_hr, age)
    # Correction âge (déclin ~1% par an après 25 ans)
    if age > 25:
        vo2max *= (1 - 0.01 * (age - 25))

    marathon_sec = _vdot_to_marathon(vo2max, gender)
    predictions = []
    for name, dist in DISTANCES:
        if dist == 42.195:
            t = marathon_sec
        else:
            t = _riegel(marathon_sec, 42.195, dist)
        predictions.append({
            "distance": name,
            "seconds": t,
            "formatted": _seconds_to_formatted(t)
        })

    return {
        "mode": "simple",
        "predictions": predictions,
        "vo2max_estimated": round(vo2max, 1),
        "method": "Formule Uth (FC repos→VO2max) + VDOT Jack Daniels + Riegel",
        "confidence": "low",
        "disclaimer": (
            "Prédiction basée sur des formules physiologiques (sans temps de course de référence). "
            "Précision indicative ±15-20%. Pour une prédiction plus précise, utilisez le mode avancé."
        )
    }

def predict_advanced(age: int, gender: int,
                     recent_5k_seconds: int = None,
                     recent_10k_seconds: int = None):
    model = _load_model()

    # Choisir la référence la plus précise (10K > 5K)
    if recent_10k_seconds is not None:
        ref_sec = recent_10k_seconds
        ref_dist = 10.0
        speed = ref_dist / (ref_sec / 3600)
        features = pd.DataFrame(
            [[age, gender, ref_sec, speed]],
            columns=["Age", "gender", "10K_sec", "speed_10k"]
        )
        # Le modèle a été entraîné sur 5K features — on extrapole le 5K depuis le 10K
        t5k = _riegel(ref_sec, 10.0, 5.0)
        speed_5k = 5.0 / (t5k / 3600)
        features = pd.DataFrame(
            [[age, gender, t5k, speed_5k]],
            columns=["Age", "gender", "5K_sec", "speed_5k"]
        )
    else:
        ref_sec = recent_5k_seconds
        speed_5k = 5.0 / (ref_sec / 3600)
        features = pd.DataFrame(
            [[age, gender, ref_sec, speed_5k]],
            columns=["Age", "gender", "5K_sec", "speed_5k"]
        )

    marathon_sec = int(model.predict(features)[0])

    predictions = []
    for name, dist in DISTANCES:
        if dist == 42.195:
            t = marathon_sec
        else:
            t = _riegel(marathon_sec, 42.195, dist)
        predictions.append({
            "distance": name,
            "seconds": t,
            "formatted": _seconds_to_formatted(t)
        })

    # VO2max estimé depuis la vitesse 5K (Jack Daniels)
    speed_5k_kmh = 5.0 / (recent_5k_seconds / 3600) if recent_5k_seconds else None
    vo2max = round(speed_5k_kmh * 3.5, 1) if speed_5k_kmh else None

    return {
        "mode": "advanced",
        "predictions": predictions,
        "vo2max_estimated": vo2max,
        "method": "Gradient Boosting (Boston Marathon 2015-2017) + Riegel",
        "confidence": "high",
        "disclaimer": None
    }
