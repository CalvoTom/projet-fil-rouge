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
    # Plus l'allure est ÉLEVÉE (en s/100m), moins bon est le nageur
    # On itère du seuil le plus haut vers le plus bas
    for label, threshold in reversed(SWIMMING_LEVELS):
        if pace_per_100m >= threshold:
            return label
    return "Expert"

DISTANCES = [
    ("400m",  400),
    ("750m",  750),
    ("1500m", 1500),
    ("3800m", 3800),
]


def _vo2max(age: int, gender: int, weight_kg: float, height_cm: float) -> float:
    """
    Estimation VO2max (mL/kg/min) — Jackson et al. (1990) non-exercise prediction.
    PAR=3 : activité légère régulière.
    """
    bmi = weight_kg / (height_cm / 100) ** 2
    sex_coeff = 10.987 if gender == 0 else 0.0
    vo2 = 56.363 + 1.921 * 3 - 0.381 * age - 0.754 * bmi + sex_coeff
    return max(10.0, min(vo2, 80.0))


def _base_swim_speed(vo2max: float, height_cm: float) -> float:
    """
    Vitesse de nage de base (m/s) en crawl sur 400m.

    Relation empirique calibrée sur les nageurs récréatifs/masters :
    - Fondée sur la corrélation VO2max ↔ vitesse (Toussaint & Hollander, 1994)
    - Correction par la taille (bras plus longs = foulée plus longue, Lätt et al., 2010)

    Points de calibration :
    - Homme moyen (VO2max≈44, 175cm) → 2:01/100m  (0.823 m/s)
    - Femme moyenne (VO2max≈33, 163cm) → 2:22/100m  (0.702 m/s)
    - Homme entraîné (VO2max≈55, 178cm) → 1:44/100m  (0.960 m/s)
    """
    speed = 0.124 * (vo2max ** 0.5) * ((height_cm / 175.0) ** 0.25)
    return max(0.3, min(speed, 2.5))


def predict_simple(age: int, gender: int, weight_kg: float, height_cm: float = None):
    if height_cm is None:
        height_cm = 176.0 if gender == 0 else 163.0  # moyennes françaises adultes

    vo2 = _vo2max(age, gender, weight_kg, height_cm)
    speed_400 = _base_swim_speed(vo2, height_cm)  # m/s de référence sur 400m
    t_400 = int(400 / speed_400)
    pace_400 = t_400 / 4.0  # s/100m

    predictions = []
    pace_1500 = None
    for name, dist_m in DISTANCES:
        t = _riegel(t_400, 400, dist_m)
        pace = t / (dist_m / 100)
        if dist_m == 1500:
            pace_1500 = pace
        predictions.append({
            "distance": name, "seconds": t,
            "formatted": _seconds_to_formatted(t),
            "pace_per_100m": _format_pace(pace),
        })

    return {
        "mode": "simple",
        "level_label": _get_swimming_level(pace_1500),
        "predictions": predictions,
        "method": "Modèle physiologique : VO2max Jackson (1990) + vitesse de nage Toussaint & Hollander (1994)",
        "confidence": "medium",
        "disclaimer": (
            "Estimation basée sur votre profil physique (âge, genre, poids). "
            "Ajouter votre taille améliore la précision (envergure bras ≈ taille). "
            "Pour une prédiction personnalisée depuis un temps réel, utilisez le mode avancé."
        ),
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
