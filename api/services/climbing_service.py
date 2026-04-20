import joblib
import numpy as np
import pandas as pd
from pathlib import Path

MODELS_DIR = Path(__file__).parent.parent.parent / "models"
_model = None
_level_config = None

def _load():
    global _model, _level_config
    if _model is None:
        _model = joblib.load(MODELS_DIR / "climbing_model.pkl")
        _level_config = joblib.load(MODELS_DIR / "climbing_level_config.pkl")

FEATURES = ["sex", "height", "weight", "bmi", "age", "years_cl"]

def _potential_mode(weight_kg: float, height_cm: float, age: int,
                    dead_hang_sec: int = None, max_pullups: int = None) -> dict:
    bmi = weight_kg / (height_cm / 100) ** 2
    score = 0

    if bmi < 20:     score += 3
    elif bmi < 22:   score += 2
    elif bmi < 25:   score += 1

    if dead_hang_sec is not None:
        if dead_hang_sec >= 60:   score += 3
        elif dead_hang_sec >= 40: score += 2
        elif dead_hang_sec >= 20: score += 1

    if max_pullups is not None:
        if max_pullups >= 15:   score += 3
        elif max_pullups >= 10: score += 2
        elif max_pullups >= 5:  score += 1

    if 20 <= age <= 30:
        score += 1

    if score <= 2:   level = 0
    elif score <= 5: level = 1
    elif score <= 8: level = 2
    else:            level = 3

    _load()
    labels = _level_config["labels"]
    ranges = _level_config["ranges"]

    return {
        "mode_used": "potential",
        "level_class": level,
        "level_label": labels[level],
        "grade_range": f"{ranges[level]['min_fra']} → {ranges[level]['max_fra']}",
        "confidence": "low",
        "probabilities": None,
        "disclaimer": (
            "Estimation basée sur votre profil physique uniquement. "
            "Votre niveau réel dépendra de votre entraînement, technique et régularité. "
            "Cette fourchette représente un potentiel après 1-2 ans de pratique sérieuse."
        )
    }

def predict(gender: int, height_cm: float, weight_kg: float, age: int,
            years_climbing: float, dead_hang_seconds: int = None,
            max_pullups: int = None) -> dict:
    _load()

    if years_climbing == 0:
        return _potential_mode(weight_kg, height_cm, age, dead_hang_seconds, max_pullups)

    bmi = weight_kg / (height_cm / 100) ** 2
    features = pd.DataFrame(
        [[gender, height_cm, weight_kg, bmi, age, years_climbing]],
        columns=FEATURES
    )

    level_pred = int(_model.predict(features)[0])
    proba = _model.predict_proba(features)[0]
    confidence = "high" if proba.max() >= 0.5 else "medium"

    labels = _level_config["labels"]
    ranges = _level_config["ranges"]

    return {
        "mode_used": "ml",
        "level_class": level_pred,
        "level_label": labels[level_pred],
        "grade_range": f"{ranges[level_pred]['min_fra']} → {ranges[level_pred]['max_fra']}",
        "confidence": confidence,
        "probabilities": {labels[i]: round(float(p), 3) for i, p in enumerate(proba)},
        "disclaimer": (
            "Moins d'un an de pratique — prédiction indicative."
            if years_climbing < 1 else None
        )
    }
