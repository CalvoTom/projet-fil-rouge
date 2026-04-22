"""Script de réentraînement des 4 modèles (Python 3.14 / sklearn 1.7.x)."""
import json
import pickle
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score, accuracy_score

MODELS_DIR = Path("models")
DATA_DIR = Path("data/processed")


# ── RUNNING ────────────────────────────────────────────────────────────────────

def train_running():
    print("\n=== RUNNING ===")
    df = pd.read_csv(DATA_DIR / "running_clean.csv").dropna(
        subset=["Age", "gender", "5K_sec", "Official Time_sec"]
    )
    df["speed_5k"] = 5.0 / (df["5K_sec"] / 3600)
    features = ["Age", "gender", "5K_sec", "speed_5k"]
    target = "Official Time_sec"

    X, y = df[features], df[target]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = GradientBoostingRegressor(n_estimators=200, max_depth=5, learning_rate=0.1,
                                      random_state=42)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    r2 = r2_score(y_test, preds)
    mape = np.mean(np.abs((y_test - preds) / y_test)) * 100

    print(f"  MAE: {mae/60:.1f} min | MAPE: {mape:.2f}% | R²: {r2:.4f}")

    joblib.dump(model, MODELS_DIR / "running_model.pkl")

    meta = {
        "model_type": "Gradient Boosting",
        "sport": "running",
        "features": features,
        "target": target,
        "metrics": {"mae_minutes": round(mae/60, 1), "mape_pct": round(mape, 2), "r2": round(r2, 4)},
        "dataset": "Boston Marathon 2015-2017",
        "trained_at": datetime.now().isoformat(),
    }
    (MODELS_DIR / "running_metadata.json").write_text(json.dumps(meta, indent=2))
    print("  Saved running_model.pkl")


# ── CLIMBING ───────────────────────────────────────────────────────────────────

CLIMBING_LABELS = [
    "Débutant (< 6a)",
    "Intermédiaire bas (6a–6b+)",
    "Intermédiaire (6c–7a+)",
    "Avancé (7b–7c+)",
    "Expert (8a+)",
]
CLIMBING_RANGES = [
    {"min_fra": "5a", "max_fra": "6a"},
    {"min_fra": "6a", "max_fra": "6b+"},
    {"min_fra": "6c", "max_fra": "7a+"},
    {"min_fra": "7b", "max_fra": "7c+"},
    {"min_fra": "8a", "max_fra": "8c+"},
]

def _grade_to_level(g: int) -> int:
    if g < 37:  return 0   # < 6a
    if g <= 43: return 1   # 6a – 6b+
    if g <= 51: return 2   # 6c – 7a+
    if g <= 60: return 3   # 7b – 7c+
    return 4               # 8a+


def train_climbing():
    print("\n=== CLIMBING ===")
    df = pd.read_csv(DATA_DIR / "climbing_clean.csv").dropna(
        subset=["sex", "height", "weight", "bmi", "age", "years_cl", "grades_max"]
    )
    df["level_class"] = df["grades_max"].apply(_grade_to_level)
    features = ["sex", "height", "weight", "bmi", "age", "years_cl"]

    X, y = df[features], df["level_class"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = GradientBoostingClassifier(n_estimators=200, max_depth=4, learning_rate=0.1,
                                       random_state=42)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)
    within1 = np.mean(np.abs(y_test - preds) <= 1) * 100

    print(f"  Accuracy: {acc:.4f} | Within-1: {within1:.1f}%")

    joblib.dump(model, MODELS_DIR / "climbing_model.pkl")

    level_config = {"labels": CLIMBING_LABELS, "ranges": CLIMBING_RANGES}
    joblib.dump(level_config, MODELS_DIR / "climbing_level_config.pkl")

    # grade_map: numeric → fra string (from dataset)
    grade_map_df = (df[["grades_max", "grade_fra"]].drop_duplicates()
                    .sort_values("grades_max").set_index("grades_max")["grade_fra"])
    grade_map = grade_map_df.to_dict()
    joblib.dump(grade_map, MODELS_DIR / "climbing_grade_map.pkl")

    meta = {
        "model_type": "Gradient Boosting",
        "problem_type": "classification",
        "sport": "climbing",
        "features": features,
        "target": "level_class (0-4)",
        "level_labels": CLIMBING_LABELS,
        "level_ranges": CLIMBING_RANGES,
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "metrics": {
            "accuracy": round(acc, 4),
            "within_1_class_pct": round(within1, 1),
        },
        "dataset": "jordizar/climb-dataset (8a.nu)",
        "trained_at": datetime.now().isoformat(),
    }
    (MODELS_DIR / "climbing_metadata.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    print("  Saved climbing_model.pkl, climbing_level_config.pkl, climbing_grade_map.pkl")


# ── CYCLING ────────────────────────────────────────────────────────────────────

def train_cycling():
    print("\n=== CYCLING ===")
    df = pd.read_csv(DATA_DIR / "cycling_clean.csv").dropna(
        subset=["age", "gender", "dist_km", "speed_kmh"]
    )
    df = df[(df["speed_kmh"] >= 5) & (df["speed_kmh"] <= 60)]

    features = ["age", "gender", "dist_km"]
    target = "speed_kmh"

    X, y = df[features], df[target]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = GradientBoostingRegressor(n_estimators=100, max_depth=4, learning_rate=0.1,
                                      subsample=0.5, random_state=42)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    r2 = r2_score(y_test, preds)
    mape = np.mean(np.abs((y_test - preds) / y_test)) * 100

    print(f"  MAE: {mae:.2f} km/h | MAPE: {mape:.2f}% | R²: {r2:.4f}")

    joblib.dump(model, MODELS_DIR / "cycling_model.pkl")

    meta = {
        "sport": "cycling",
        "model": "GradientBoostingRegressor",
        "target": target,
        "features": features,
        "dataset": "vladislavboyadzhi/triathlon-results",
        "n_train": len(X_train),
        "n_test": len(X_test),
        "mae_kmh": round(mae, 2),
        "mape_pct": round(mape, 2),
        "r2": round(r2, 4),
        "trained_at": datetime.now().isoformat(),
    }
    (MODELS_DIR / "cycling_metadata.json").write_text(json.dumps(meta, indent=2))
    print("  Saved cycling_model.pkl")


# ── SWIMMING ───────────────────────────────────────────────────────────────────

def train_swimming():
    print("\n=== SWIMMING ===")
    df = pd.read_csv(DATA_DIR / "swimming_clean.csv").dropna(
        subset=["age", "gender", "dist_m", "pace_per_100m"]
    )
    df = df[(df["pace_per_100m"] >= 40) & (df["pace_per_100m"] <= 400)]

    features = ["age", "gender", "dist_m"]
    target = "pace_per_100m"

    X, y = df[features], df[target]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = GradientBoostingRegressor(n_estimators=100, max_depth=4, learning_rate=0.1,
                                      subsample=0.5, random_state=42)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    r2 = r2_score(y_test, preds)
    mape = np.mean(np.abs((y_test - preds) / y_test)) * 100

    print(f"  MAE: {mae:.2f} s/100m | MAPE: {mape:.2f}% | R²: {r2:.4f}")

    joblib.dump(model, MODELS_DIR / "swimming_model.pkl")

    meta = {
        "sport": "swimming",
        "model": "GradientBoostingRegressor",
        "target": target,
        "features": features,
        "dataset": "vladislavboyadzhi/triathlon-results",
        "n_train": len(X_train),
        "n_test": len(X_test),
        "mae_sec_per_100m": round(mae, 2),
        "mape_pct": round(mape, 2),
        "r2": round(r2, 4),
        "trained_at": datetime.now().isoformat(),
    }
    (MODELS_DIR / "swimming_metadata.json").write_text(json.dumps(meta, indent=2))
    print("  Saved swimming_model.pkl")


if __name__ == "__main__":
    train_running()
    train_climbing()
    train_cycling()
    train_swimming()
    print("\n✓ Tous les modèles ont été réentraînés et sauvegardés.")
