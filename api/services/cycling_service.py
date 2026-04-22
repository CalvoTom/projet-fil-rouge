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


def _vo2max(age: int, gender: int, weight_kg: float, height_cm: float) -> float:
    """
    Estimation VO2max (mL/kg/min) — Jackson et al. (1990) non-exercise prediction.
    PAR=3 : activité physique légère régulière (profil "mode simple").
    """
    bmi = weight_kg / (height_cm / 100) ** 2
    sex_coeff = 10.987 if gender == 0 else 0.0
    vo2 = 56.363 + 1.921 * 3 - 0.381 * age - 0.754 * bmi + sex_coeff
    return max(10.0, min(vo2, 80.0))


def _ftp_watts(vo2max: float, weight_kg: float) -> float:
    """
    FTP (Watts) depuis VO2max.
    Relation linéaire validée : FTP/kg ≈ 0.055 × VO2max − 0.5 (Coggan, 2003).
    """
    ftp_per_kg = max(0.5, 0.055 * vo2max - 0.5)
    return ftp_per_kg * weight_kg


def _cda(weight_kg: float) -> float:
    """
    Coefficient aérodynamique CdA (m²) estimé depuis le poids.
    Cycliste en position sur le guidon : CdA ≈ 0.32 + correction poids.
    """
    return 0.32 + 0.001 * max(0.0, weight_kg - 70)


def _solve_cycling_speed(power_w: float, mass_kg: float, cda: float,
                          crr: float = 0.004, rho: float = 1.225, g: float = 9.81) -> float:
    """Résolution numérique de P = CdA·½ρv³ + Crr·m·g·v par bisection."""
    v_lo, v_hi = 0.5, 30.0
    for _ in range(60):
        v_mid = (v_lo + v_hi) / 2
        p_mid = cda * 0.5 * rho * v_mid ** 3 + crr * mass_kg * g * v_mid
        if p_mid < power_w:
            v_lo = v_mid
        else:
            v_hi = v_mid
    return (v_lo + v_hi) / 2


_POWER_FACTORS = {20.0: 0.90, 40.0: 0.85, 100.0: 0.78, 180.0: 0.72}


def predict_simple(age: int, gender: int, weight_kg: float, height_cm: float = None):
    if height_cm is None:
        height_cm = 176.0 if gender == 0 else 163.0  # moyennes françaises adultes

    vo2 = _vo2max(age, gender, weight_kg, height_cm)
    ftp = _ftp_watts(vo2, weight_kg)
    cda = _cda(weight_kg)

    predictions = []
    speed_40k = None
    for name, dist_km in DISTANCES:
        pwr = ftp * _POWER_FACTORS[dist_km]
        speed_mps = _solve_cycling_speed(pwr, weight_kg, cda)
        speed_kmh = round(min(60.0, max(6.0, speed_mps * 3.6)), 1)
        t = int((dist_km / speed_kmh) * 3600)
        if dist_km == 40.0:
            speed_40k = speed_kmh
        predictions.append({
            "distance": name, "seconds": t,
            "formatted": _seconds_to_formatted(t), "speed_kmh": speed_kmh,
        })

    return {
        "mode": "simple",
        "level_label": _get_cycling_level(speed_40k),
        "predictions": predictions,
        "method": "Modèle physiologique : VO2max Jackson (1990) + physique du vélo (Bassett & Howley, 2000)",
        "confidence": "medium",
        "disclaimer": (
            "Estimation basée sur votre profil physique (âge, genre, poids). "
            "Ajouter votre taille améliore la précision. "
            "Pour une prédiction personnalisée depuis un temps réel, utilisez le mode avancé."
        ),
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
