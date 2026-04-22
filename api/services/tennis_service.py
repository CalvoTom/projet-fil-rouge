import joblib
import numpy as np
import pandas as pd
from pathlib import Path

MODELS_DIR = Path(__file__).parent.parent.parent / "models"

_model_simple   = None
_model_advanced = None
_level_config   = None


def _load():
    global _model_simple, _model_advanced, _level_config
    if _model_simple is None:
        _model_simple   = joblib.load(MODELS_DIR / "tennis_model_simple.pkl")
        _model_advanced = joblib.load(MODELS_DIR / "tennis_model_advanced.pkl")
        _level_config   = joblib.load(MODELS_DIR / "tennis_level_config.pkl")


def _format_result(level_class: int, proba: np.ndarray, mode: str,
                   method: str, disclaimer: str = None) -> dict:
    _load()
    cfg = _level_config
    confidence = (
        "high"   if proba.max() >= 0.60 else
        "medium" if proba.max() >= 0.40 else
        "low"
    )
    labels = cfg["labels"]
    return {
        "sport":            "tennis",
        "mode":             mode,
        "level_class":      int(level_class),
        "level_label":      labels[level_class],
        "level_equiv":      cfg["equiv"][level_class],
        "level_rank_range": cfg["rank_range"][level_class],
        "confidence":       confidence,
        "probabilities":    {labels[i]: round(float(p), 3) for i, p in enumerate(proba)},
        "ref_stats":        cfg["ref_stats"][level_class],
        "method":           method,
        "disclaimer":       disclaimer,
    }


def predict_simple(age: int, gender: int, height_cm: float,
                   years_practice: float) -> dict:
    _load()
    features = pd.DataFrame(
        [[age, gender, height_cm, years_practice]],
        columns=["age", "gender", "height", "years_pro"],
    )
    level = int(_model_simple.predict(features)[0])
    proba = _model_simple.predict_proba(features)[0]

    return _format_result(
        level_class=level,
        proba=proba,
        mode="simple",
        method="GradientBoosting — profil physique + expérience (ATP/WTA 2010-2023)",
        disclaimer=(
            "Estimation basée sur l'âge, la taille et les années de pratique. "
            "Le modèle est entraîné sur des joueurs de circuit professionnel ; "
            "pour les joueurs amateurs, l'estimation est indicative. "
            "Utilisez le mode avancé avec vos statistiques de service pour plus de précision."
        ),
    )


def predict_advanced(gender: int, first_serve_pct: float, ace_rate: float,
                     df_rate: float, first_serve_won_pct: float,
                     second_serve_won_pct: float, bp_saved_pct: float) -> dict:
    _load()
    features = pd.DataFrame([[
        gender,
        ace_rate            / 100,
        df_rate             / 100,
        first_serve_pct     / 100,
        first_serve_won_pct / 100,
        second_serve_won_pct/ 100,
        bp_saved_pct        / 100,
    ]], columns=[
        "gender",
        "ace_rate", "df_rate", "first_serve_pct",
        "first_serve_won_pct", "second_serve_won_pct", "bp_saved_pct",
    ])
    level = int(_model_advanced.predict(features)[0])
    proba = _model_advanced.predict_proba(features)[0]

    return _format_result(
        level_class=level,
        proba=proba,
        mode="advanced",
        method="GradientBoosting — statistiques de service (ATP/WTA 2010-2023)",
        disclaimer=None,
    )
