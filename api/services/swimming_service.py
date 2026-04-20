import joblib
import numpy as np
import pandas as pd
from pathlib import Path

MODEL_PATH = Path(__file__).parent.parent.parent / "models" / "swimming_model.pkl"
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

def _format_pace(pace_sec_per_100m: float) -> str:
    m = int(pace_sec_per_100m // 60)
    s = int(pace_sec_per_100m % 60)
    return f"{m}:{s:02d}/100m"

def _riegel(t1_sec: float, d1_m: float, d2_m: float) -> int:
    return int(t1_sec * (d2_m / d1_m) ** 1.06)

# Seuils basés sur l'allure aux 100m (s/100m) — plus le chiffre est bas, meilleur c'est
SWIMMING_LEVELS = [
    ("Expert",         0),    # < 90s/100m (< 1:30)
    ("Avancé",         90),   # 90–120s
    ("Intermédiaire",  120),  # 120–150s
    ("Débutant",       150),  # > 150s
]

def _get_swimming_level(pace_per_100m: float) -> str:
    for label, threshold in SWIMMING_LEVELS:
        if pace_per_100m >= threshold:
            return label
    return "Débutant"

DISTANCES = [
    ("400m",  400),
    ("750m",  750),
    ("1500m", 1500),
    ("3800m", 3800),
]


def predict_simple(age: int, gender: int):
    model = _load_model()
    predictions = []
    pace_1500 = None
    for name, dist_m in DISTANCES:
        features = pd.DataFrame([[age, gender, dist_m]], columns=["age", "gender", "dist_m"])
        pace = float(model.predict(features)[0])
        pace = max(45.0, min(pace, 300.0))
        t = int(pace * (dist_m / 100))
        if dist_m == 1500:
            pace_1500 = pace
        predictions.append({"distance": name, "seconds": t, "formatted": _seconds_to_formatted(t),
                             "pace_per_100m": _format_pace(pace)})

    return {
        "mode": "simple",
        "level_label": _get_swimming_level(pace_1500),
        "predictions": predictions,
        "method": "Gradient Boosting (triathlon Sprint/Olympic/Half/Full — tous niveaux) + profil âge/genre",
        "confidence": "low",
        "disclaimer": (
            "Prédiction basée sur votre profil (âge, genre) uniquement. "
            "Pour une estimation personnalisée, utilisez le mode avancé avec un temps de référence."
        )
    }


def predict_advanced(age: int, gender: int, ref_distance_m: int, ref_time_seconds: int):
    pace_ref = ref_time_seconds / (ref_distance_m / 100)

    # Normaliser l'allure sur 1500m pour le niveau
    t_1500 = _riegel(ref_time_seconds, ref_distance_m, 1500)
    pace_1500 = t_1500 / 15.0

    predictions = []
    for name, dist_m in DISTANCES:
        t = _riegel(ref_time_seconds, ref_distance_m, dist_m)
        pace = t / (dist_m / 100)
        predictions.append({"distance": name, "seconds": t, "formatted": _seconds_to_formatted(t),
                             "pace_per_100m": _format_pace(pace)})

    return {
        "mode": "advanced",
        "level_label": _get_swimming_level(pace_1500),
        "predictions": predictions,
        "method": "Formule Riegel (D₂/D₁)^1.06 depuis temps de référence",
        "confidence": "high",
        "disclaimer": None
    }
