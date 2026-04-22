"""
Tennis — EDA + Feature Engineering + Modèles
Sources : Jeff Sackmann ATP/WTA 2010-2023
https://github.com/JeffSackmann/tennis_atp
https://github.com/JeffSackmann/tennis_wta

Cibles :
  - Modèle SIMPLE   : age, gender, height_cm, years_pro → level_class
  - Modèle AVANCÉ   : ace_rate, df_rate, first_serve_pct,
                      first_serve_won_pct, second_serve_won_pct,
                      bp_saved_pct, gender → level_class

Level classes :
  0 — Débutant circuit   (rank > 500)
  1 — Intermédiaire      (rank 201-500)
  2 — Avancé             (rank 51-200)
  3 — Expert / Top 50    (rank ≤ 50)
"""

import json
import warnings
from datetime import datetime
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import (accuracy_score, classification_report,
                             confusion_matrix)
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.preprocessing import LabelEncoder

warnings.filterwarnings("ignore")

RAW   = Path("data/raw/tennis")
PROC  = Path("data/processed")
MDIR  = Path("models")

# ─────────────────────────────────────────────────────────────────────────────
# 1. CHARGEMENT DES DONNÉES
# ─────────────────────────────────────────────────────────────────────────────

def load_matches(pattern, gender_val):
    files = sorted(RAW.glob(pattern))
    frames = []
    for f in files:
        df = pd.read_csv(f, low_memory=False)
        df["gender"] = gender_val
        df["year"] = int(str(f.stem).split("_")[-1])
        frames.append(df)
    return pd.concat(frames, ignore_index=True)

print("Chargement ATP (homme=0) …")
atp = load_matches("atp_matches_*.csv", gender_val=0)
print(f"  ATP : {len(atp):,} matchs")

print("Chargement WTA (femme=1) …")
wta = load_matches("wta_matches_*.csv", gender_val=1)
print(f"  WTA : {len(wta):,} matchs")

# ─────────────────────────────────────────────────────────────────────────────
# 2. EXTRACTION D'UNE LIGNE PAR JOUEUR × MATCH (vainqueur ET perdant)
# ─────────────────────────────────────────────────────────────────────────────

def extract_player_rows(df, gender_val):
    """Transforme un dataframe de matchs en une ligne par joueur par match."""
    rows = []
    for side, s_won in [("winner", 1), ("loser", 0)]:
        s = "w" if side == "winner" else "l"
        tmp = df[[
            f"{side}_id", f"{side}_name", f"{side}_age", f"{side}_ht",
            f"{side}_rank", f"{side}_rank_points",
            f"{s}_ace", f"{s}_df", f"{s}_svpt",
            f"{s}_1stIn", f"{s}_1stWon", f"{s}_2ndWon",
            f"{s}_bpSaved", f"{s}_bpFaced",
            "gender", "year", "surface",
        ]].copy()
        tmp.columns = [
            "player_id", "player_name", "age", "height",
            "rank", "rank_points",
            "ace", "df", "svpt", "first_in", "first_won", "second_won",
            "bp_saved", "bp_faced",
            "gender", "year", "surface",
        ]
        tmp["won"] = s_won
        rows.append(tmp)

    return pd.concat(rows, ignore_index=True)


print("\nExtraction des lignes joueur …")
player_rows = pd.concat([
    extract_player_rows(atp, 0),
    extract_player_rows(wta, 1),
], ignore_index=True)
print(f"  Lignes totales : {len(player_rows):,}")

# ─────────────────────────────────────────────────────────────────────────────
# 3. FEATURE ENGINEERING
# ─────────────────────────────────────────────────────────────────────────────

# Filtres de qualité
player_rows = player_rows[player_rows["svpt"] >= 10]
player_rows = player_rows[player_rows["age"].between(15, 45)]
player_rows = player_rows[player_rows["height"].between(155, 220)]
player_rows = player_rows[player_rows["rank"].between(1, 1500)]

# Ratios serve (évite div/0)
eps = 1e-6
player_rows["ace_rate"]            = player_rows["ace"]   / (player_rows["svpt"] + eps)
player_rows["df_rate"]             = player_rows["df"]    / (player_rows["svpt"] + eps)
player_rows["first_serve_pct"]     = player_rows["first_in"] / (player_rows["svpt"] + eps)
player_rows["first_serve_won_pct"] = player_rows["first_won"] / (player_rows["first_in"].clip(lower=1))
player_rows["second_serve_won_pct"]= player_rows["second_won"] / (
    (player_rows["svpt"] - player_rows["first_in"]).clip(lower=1))
player_rows["bp_saved_pct"]        = player_rows["bp_saved"] / (player_rows["bp_faced"].clip(lower=1))

# Ancienneté pro par joueur
first_year = player_rows.groupby("player_id")["year"].min().rename("first_year")
player_rows = player_rows.join(first_year, on="player_id")
player_rows["years_pro"] = (player_rows["year"] - player_rows["first_year"]).clip(lower=0)

# ─────────────────────────────────────────────────────────────────────────────
# 4. AGRÉGATION PAR JOUEUR × SAISON
# ─────────────────────────────────────────────────────────────────────────────

stat_cols = [
    "age", "height", "gender",
    "rank", "rank_points",
    "ace_rate", "df_rate", "first_serve_pct",
    "first_serve_won_pct", "second_serve_won_pct", "bp_saved_pct",
    "years_pro",
]

agg = (player_rows
       .groupby(["player_id", "player_name", "year"])[stat_cols]
       .mean()
       .reset_index())

agg["rank"] = agg["rank"].round(0).astype(int)

# Target : niveau de classement
def rank_to_level(r):
    if r <= 50:   return 3   # Expert
    if r <= 200:  return 2   # Avancé
    if r <= 500:  return 1   # Intermédiaire
    return 0                  # Débutant circuit

agg["level_class"] = agg["rank"].apply(rank_to_level)

print(f"\nDataset agrégé : {len(agg):,} lignes (joueur×saison)")
print(agg["level_class"].value_counts().sort_index())

# Sauvegarder CSV nettoyé
agg.to_csv(PROC / "tennis_clean.csv", index=False)
print(f"Sauvegardé → data/processed/tennis_clean.csv")

# ─────────────────────────────────────────────────────────────────────────────
# 5. EDA
# ─────────────────────────────────────────────────────────────────────────────

fig, axes = plt.subplots(2, 3, figsize=(15, 8))
fig.suptitle("Tennis — EDA", fontsize=14, fontweight="bold")

level_labels = {0: "Débutant circuit", 1: "Intermédiaire", 2: "Avancé", 3: "Expert"}
agg["level_label"] = agg["level_class"].map(level_labels)

axes[0,0].set_title("Distribution des niveaux")
agg["level_class"].value_counts().sort_index().plot(kind="bar", ax=axes[0,0], color="#4C72B0")
axes[0,0].set_xticklabels([level_labels[i] for i in range(4)], rotation=20)

axes[0,1].set_title("% 1ère balle entrée par niveau")
for lv, grp in agg.groupby("level_class"):
    axes[0,1].hist(grp["first_serve_pct"], alpha=0.5, bins=30, label=level_labels[lv])
axes[0,1].legend(fontsize=7)

axes[0,2].set_title("Ace rate par niveau")
agg.boxplot(column="ace_rate", by="level_class", ax=axes[0,2])
axes[0,2].set_xticklabels([level_labels[i] for i in range(4)], rotation=20)
axes[0,2].set_title("Ace rate par niveau")

axes[1,0].set_title("Taille par niveau")
agg.boxplot(column="height", by="level_class", ax=axes[1,0])
axes[1,0].set_xticklabels([level_labels[i] for i in range(4)], rotation=20)
axes[1,0].set_title("Taille par niveau")

axes[1,1].set_title("Années pro par niveau")
agg.boxplot(column="years_pro", by="level_class", ax=axes[1,1])
axes[1,1].set_xticklabels([level_labels[i] for i in range(4)], rotation=20)
axes[1,1].set_title("Années pro par niveau")

axes[1,2].set_title("Corrélations (features avancé)")
adv_cols = ["ace_rate","df_rate","first_serve_pct","first_serve_won_pct",
            "second_serve_won_pct","bp_saved_pct","level_class"]
corr = agg[adv_cols].corr()
sns.heatmap(corr, ax=axes[1,2], annot=True, fmt=".2f", cmap="coolwarm", cbar=False)

plt.tight_layout()
plt.savefig(PROC / "tennis_eda.png", dpi=120, bbox_inches="tight")
plt.close()
print("EDA sauvegardée → data/processed/tennis_eda.png")

# ─────────────────────────────────────────────────────────────────────────────
# 6. MODÈLE SIMPLE  (age, gender, height, years_pro → level)
# ─────────────────────────────────────────────────────────────────────────────

print("\n─── MODÈLE SIMPLE ───")
FEATS_SIMPLE = ["age", "gender", "height", "years_pro"]

df_s = agg[FEATS_SIMPLE + ["level_class"]].dropna()
X_s, y_s = df_s[FEATS_SIMPLE], df_s["level_class"]

X_tr_s, X_te_s, y_tr_s, y_te_s = train_test_split(
    X_s, y_s, test_size=0.2, random_state=42, stratify=y_s)

model_simple = GradientBoostingClassifier(
    n_estimators=300, max_depth=4, learning_rate=0.08,
    subsample=0.8, min_samples_leaf=20, random_state=42)
model_simple.fit(X_tr_s, y_tr_s)

preds_s = model_simple.predict(X_te_s)
acc_s   = accuracy_score(y_te_s, preds_s)
w1_s    = np.mean(np.abs(y_te_s - preds_s) <= 1) * 100
cv_s    = cross_val_score(model_simple, X_s, y_s, cv=5, scoring="accuracy")

print(f"  Accuracy test  : {acc_s:.4f}")
print(f"  Within-1 class : {w1_s:.1f}%")
print(f"  CV (5-fold)    : {cv_s.mean():.4f} ± {cv_s.std():.4f}")
print(classification_report(y_te_s, preds_s,
      target_names=[level_labels[i] for i in range(4)]))

joblib.dump(model_simple, MDIR / "tennis_model_simple.pkl")

# ─────────────────────────────────────────────────────────────────────────────
# 7. MODÈLE AVANCÉ  (stats de service → level)
# ─────────────────────────────────────────────────────────────────────────────

print("\n─── MODÈLE AVANCÉ ───")
FEATS_ADV = [
    "gender",
    "ace_rate", "df_rate", "first_serve_pct",
    "first_serve_won_pct", "second_serve_won_pct", "bp_saved_pct",
]

df_a = agg[FEATS_ADV + ["level_class"]].dropna()
X_a, y_a = df_a[FEATS_ADV], df_a["level_class"]

X_tr_a, X_te_a, y_tr_a, y_te_a = train_test_split(
    X_a, y_a, test_size=0.2, random_state=42, stratify=y_a)

model_adv = GradientBoostingClassifier(
    n_estimators=400, max_depth=5, learning_rate=0.07,
    subsample=0.8, min_samples_leaf=15, random_state=42)
model_adv.fit(X_tr_a, y_tr_a)

preds_a = model_adv.predict(X_te_a)
acc_a   = accuracy_score(y_te_a, preds_a)
w1_a    = np.mean(np.abs(y_te_a - preds_a) <= 1) * 100
cv_a    = cross_val_score(model_adv, X_a, y_a, cv=5, scoring="accuracy")

print(f"  Accuracy test  : {acc_a:.4f}")
print(f"  Within-1 class : {w1_a:.1f}%")
print(f"  CV (5-fold)    : {cv_a.mean():.4f} ± {cv_a.std():.4f}")
print(classification_report(y_te_a, preds_a,
      target_names=[level_labels[i] for i in range(4)]))

joblib.dump(model_adv, MDIR / "tennis_model_advanced.pkl")

# ─────────────────────────────────────────────────────────────────────────────
# 8. CONFIG NIVEAUX + STATS DE RÉFÉRENCE
# ─────────────────────────────────────────────────────────────────────────────

LEVEL_LABELS = [
    "Joueur de club",
    "Compétiteur régional",
    "Joueur national",
    "Expert / Pro",
]
LEVEL_EQUIV = [
    "Classement national : 30/1 – 15/1",
    "Classement national : 4/6 – 0",
    "Classement national : -2/6 – -15",
    "Classement ATP/WTA (≤ 200)",
]
LEVEL_RANK_RANGE = [
    "> 500 ATP/WTA",
    "201–500 ATP/WTA",
    "51–200 ATP/WTA",
    "≤ 50 ATP/WTA",
]

# Stats moyennes par niveau (pour affichage dans l'UI)
ref_stats = {}
for lv in range(4):
    sub = agg[agg["level_class"] == lv]
    ref_stats[lv] = {
        "first_serve_pct":      round(sub["first_serve_pct"].mean() * 100, 1),
        "ace_rate":             round(sub["ace_rate"].mean() * 100, 1),
        "df_rate":              round(sub["df_rate"].mean() * 100, 1),
        "first_serve_won_pct":  round(sub["first_serve_won_pct"].mean() * 100, 1),
        "second_serve_won_pct": round(sub["second_serve_won_pct"].mean() * 100, 1),
        "bp_saved_pct":         round(sub["bp_saved_pct"].mean() * 100, 1),
    }

level_config = {
    "labels":       LEVEL_LABELS,
    "equiv":        LEVEL_EQUIV,
    "rank_range":   LEVEL_RANK_RANGE,
    "ref_stats":    ref_stats,
    "features_simple":  FEATS_SIMPLE,
    "features_advanced": FEATS_ADV,
}
joblib.dump(level_config, MDIR / "tennis_level_config.pkl")

# ─────────────────────────────────────────────────────────────────────────────
# 9. MÉTADONNÉES
# ─────────────────────────────────────────────────────────────────────────────

meta = {
    "sport": "tennis",
    "models": {
        "simple": {
            "file": "tennis_model_simple.pkl",
            "type": "GradientBoostingClassifier",
            "features": FEATS_SIMPLE,
            "accuracy": round(acc_s, 4),
            "within_1_class_pct": round(w1_s, 1),
            "cv_accuracy_mean": round(cv_s.mean(), 4),
        },
        "advanced": {
            "file": "tennis_model_advanced.pkl",
            "type": "GradientBoostingClassifier",
            "features": FEATS_ADV,
            "accuracy": round(acc_a, 4),
            "within_1_class_pct": round(w1_a, 1),
            "cv_accuracy_mean": round(cv_a.mean(), 4),
        },
    },
    "target": "level_class (0-3)",
    "level_labels": LEVEL_LABELS,
    "level_rank_range": LEVEL_RANK_RANGE,
    "n_player_seasons": len(agg),
    "dataset": "JeffSackmann ATP+WTA 2010-2023 (github.com/JeffSackmann)",
    "trained_at": datetime.now().isoformat(),
    "note": (
        "Entraîné sur des joueurs de circuit professionnel ATP/WTA. "
        "Le modèle capture les patterns physiques et de service qui différencient "
        "les niveaux de jeu. Pour les joueurs amateurs, extrapolation indicative."
    ),
}
(MDIR / "tennis_metadata.json").write_text(
    json.dumps(meta, indent=2, ensure_ascii=False))

print(f"\n✓ Modèles sauvegardés dans models/")
print(f"  tennis_model_simple.pkl   — accuracy {acc_s:.4f}")
print(f"  tennis_model_advanced.pkl — accuracy {acc_a:.4f}")
print(f"  tennis_level_config.pkl")
print(f"  tennis_metadata.json")
