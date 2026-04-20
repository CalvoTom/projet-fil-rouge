import joblib
import numpy as np
import pandas as pd
from pathlib import Path

MODEL_PATH = Path(__file__).parent.parent.parent / "models" / "cycling_model.pkl"
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

# Seuils basés sur la vitesse moyenne sur 40km (km/h)
CYCLING_LEVELS = [
    ("Débutant",       0),     # < 22 km/h
    ("Intermédiaire",  22),    # 22–28 km/h
    ("Avancé",         28),    # 28–34 km/h
    ("Expert",         34),    # > 34 km/h
]

def _get_cycling_level(speed_40k_kmh: float) -> str:
    for label, threshold in reversed(CYCLING_LEVELS):
        if speed_40k_kmh >= threshold:
            return label
    return "Débutant"

DISTANCES = [
    ("20km",  20.0),
    ("40km",  40.0),
    ("100km", 100.0),
    ("180km", 180.0),
]


def predict_simple(age: int, gender: int):
    model = _load_model()
    predictions = []
    speed_40k = None
    for name, dist_km in DISTANCES:
        features = pd.DataFrame([[age, gender, dist_km]], columns=["age", "gender", "dist_km"])
        speed = float(model.predict(features)[0])
        speed = max(8.0, min(speed, 55.0))
        t = int((dist_km / speed) * 3600)
        if dist_km == 40.0:
            speed_40k = speed
        predictions.append({"distance": name, "seconds": t, "formatted": _seconds_to_formatted(t),
                             "speed_kmh": round(speed, 1)})

    return {
        "mode": "simple",
        "level_label": _get_cycling_level(speed_40k),
        "predictions": predictions,
        "method": "Gradient Boosting (triathlon Sprint/Olympic/Half/Full — tous niveaux) + profil âge/genre",
        "confidence": "low",
        "disclaimer": (
            "Prédiction basée sur votre profil (âge, genre) uniquement. "
            "Pour une estimation personnalisée, utilisez le mode avancé avec un temps de référence."
        )
    }


def predict_advanced(age: int, gender: int, ref_distance_km: float, ref_time_seconds: int):
    ref_speed = ref_distance_km / (ref_time_seconds / 3600)

    # Référence sur 40km via Riegel
    t_40k = _riegel(ref_time_seconds, ref_distance_km, 40.0)
    speed_40k = 40.0 / (t_40k / 3600)

    predictions = []
    for name, dist_km in DISTANCES:
        t = _riegel(ref_time_seconds, ref_distance_km, dist_km)
        speed = dist_km / (t / 3600)
        predictions.append({"distance": name, "seconds": t, "formatted": _seconds_to_formatted(t),
                             "speed_kmh": round(speed, 1)})

    return {
        "mode": "advanced",
        "level_label": _get_cycling_level(speed_40k),
        "predictions": predictions,
        "method": "Formule Riegel (D₂/D₁)^1.06 depuis temps de référence",
        "confidence": "high",
        "disclaimer": None
    }
