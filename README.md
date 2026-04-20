# Projet fil rouge — Prédiction sportive

Application de data storytelling permettant de prédire des performances sportives à partir de données physiologiques personnelles.

**Formation** : Ynov Informatique — Bachelor 3 — Spécialité Data & IA  
**Auteur** : Romeo Bernard

---

## Sports couverts (V1)

- **Running** : prédiction de temps sur 5km, 10km, semi-marathon, marathon
- **Escalade** : prédiction de niveau en falaise (cotation française)

---

## Stack technique

| Composant | Technologie |
|---|---|
| Interface utilisateur | Streamlit |
| API backend | FastAPI |
| Modèles ML | scikit-learn |
| Notebooks | Jupyter |
| Données | pandas, numpy |
| Visualisations | matplotlib, seaborn, plotly |

---

## Installation

### Prérequis
- Python 3.10+
- pip

### 1. Cloner le dépôt
```bash
git clone <url-du-repo>
cd projet-fil-rouge
```

### 2. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 3. Télécharger les données
Voir `docs/data_sources.md` pour les instructions complètes.

```bash
# Nécessite un compte Kaggle et kaggle.json configuré
kaggle datasets download -d rojour/boston-results -p data/raw/running/
kaggle datasets download -d dcohen21/8anu-climbing-logbook -p data/raw/climbing/
```

### 4. Entraîner les modèles
Exécuter les notebooks dans l'ordre :
```
notebooks/01_eda_running.ipynb
notebooks/02_eda_climbing.ipynb
notebooks/03_model_running.ipynb
notebooks/04_model_climbing.ipynb
```

### 5. Lancer l'application

```bash
# Terminal 1 — API FastAPI
python3 -m uvicorn api.main:app --reload --port 8008

# Terminal 2 — Interface Streamlit
streamlit run app/main.py
```

- Interface : http://localhost:8501
- Documentation API : http://localhost:8008/docs

---

## API Quickstart

### Lancer l'API

```bash
pip install -r requirements.txt
python3 -m uvicorn api.main:app --reload --port 8008
```

---

### Running — Mode simple
*Profil physiologique uniquement, sans temps de référence.*

```bash
curl -X POST http://localhost:8008/api/v1/running/predict/simple \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "simple",
    "age": 30,
    "gender": 0,
    "resting_hr": 60,
    "max_hr": 190
  }'
```

| Champ | Type | Valeurs |
|---|---|---|
| `age` | int | 15 – 85 |
| `gender` | int | `0` = homme, `1` = femme |
| `resting_hr` | int | FC repos en bpm |
| `max_hr` | int | FC max en bpm (optionnel, estimée si absent) |

```json
{
  "sport": "running",
  "mode": "simple",
  "level_label": "Débutant",
  "predictions": [
    { "distance": "5km",           "seconds": 1680, "formatted": "28m00s" },
    { "distance": "10km",          "seconds": 3502, "formatted": "58m22s" },
    { "distance": "Semi-marathon", "seconds": 7730, "formatted": "2h08m50s" },
    { "distance": "Marathon",      "seconds": 16108,"formatted": "4h28m28s" }
  ],
  "vo2max_estimated": 46.0,
  "method": "Formule Uth (FC repos→VO2max) + VDOT Jack Daniels + Riegel",
  "confidence": "low",
  "disclaimer": "Prédiction basée sur des formules physiologiques..."
}
```

---

### Running — Mode avancé
*Avec un temps de course récent — modèle ML.*

```bash
curl -X POST http://localhost:8008/api/v1/running/predict/advanced \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "advanced",
    "age": 30,
    "gender": 0,
    "recent_5k_seconds": 1320
  }'
```

| Champ | Type | Valeurs |
|---|---|---|
| `age` | int | 15 – 85 |
| `gender` | int | `0` = homme, `1` = femme |
| `recent_5k_seconds` | int | Temps 5K en secondes (ex: 22min = `1320`) |
| `recent_10k_seconds` | int | Temps 10K en secondes — alternatif au 5K |

*Au moins un des deux temps (`5K` ou `10K`) est obligatoire.*

```json
{
  "sport": "running",
  "mode": "advanced",
  "level_label": "Avancé",
  "predictions": [
    { "distance": "5km",           "seconds": 1261, "formatted": "21m01s" },
    { "distance": "10km",          "seconds": 2630, "formatted": "43m50s" },
    { "distance": "Semi-marathon", "seconds": 5804, "formatted": "1h36m44s" },
    { "distance": "Marathon",      "seconds": 12102,"formatted": "3h21m42s" }
  ],
  "vo2max_estimated": 47.7,
  "method": "Gradient Boosting (Boston Marathon 2015-2017) + Riegel",
  "confidence": "high",
  "disclaimer": null
}
```

---

### Escalade

```bash
curl -X POST http://localhost:8008/api/v1/climbing/predict \
  -H "Content-Type: application/json" \
  -d '{
    "age": 25,
    "gender": 0,
    "height_cm": 175,
    "weight_kg": 65,
    "years_climbing": 3,
    "dead_hang_seconds": 45,
    "max_pullups": 10
  }'
```

| Champ | Type | Valeurs |
|---|---|---|
| `age` | int | 10 – 80 |
| `gender` | int | `0` = homme, `1` = femme |
| `height_cm` | float | Taille en cm |
| `weight_kg` | float | Poids en kg |
| `years_climbing` | float | Années de pratique (`0` = jamais grimpé) |
| `dead_hang_seconds` | int | Temps de suspension en secondes (optionnel) |
| `max_pullups` | int | Nombre max de tractions (optionnel) |

```json
{
  "sport": "climbing",
  "mode_used": "ml",
  "level_class": 2,
  "level_label": "Intermédiaire (6c–7a+)",
  "grade_range": "6c → 7a+",
  "confidence": "medium",
  "probabilities": {
    "Débutant (< 6a)": 0.046,
    "Intermédiaire bas (6a–6b+)": 0.187,
    "Intermédiaire (6c–7a+)": 0.367,
    "Avancé (7b–7c+)": 0.320,
    "Expert (8a+)": 0.080
  },
  "disclaimer": null
}
```

*Si `years_climbing = 0`, le champ `mode_used` vaut `"potential"` et la réponse contient une fourchette de potentiel basée sur le profil physique.*

---

### Vérifier que l'API tourne

```bash
curl http://localhost:8008/health
# {"status": "ok"}
```

Documentation interactive complète : **http://localhost:8008/docs**

---

## Structure du projet

```
projet-fil-rouge/
├── CLAUDE.md          # Contexte projet pour assistants IA
├── data/              # Données (brutes non versionnées)
├── notebooks/         # Démarche EDA + modélisation
├── models/            # Modèles entraînés (.pkl)
├── api/               # FastAPI — endpoints de prédiction
├── app/               # Streamlit — interface utilisateur
└── docs/              # Documentation technique
```

Voir `docs/architecture.md` pour le détail de l'architecture.  
Voir `docs/decisions.md` pour les choix techniques et leurs justifications.  
Voir `docs/roadmap.md` pour le planning et l'état d'avancement.

---

## Contexte académique

Ce projet est réalisé dans le cadre de l'UF Spécialité Data & IA (Ynov Bachelor 3).  
Il couvre : acquisition de données, EDA, modélisation ML, évaluation, visualisation, API, interface interactive, documentation.
