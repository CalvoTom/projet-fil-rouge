# Architecture technique

> Dernière mise à jour : 2026-04-20

---

## Vue d'ensemble

```
┌─────────────────────────────────────────────────┐
│                  Streamlit App                  │
│  (Interface utilisateur — pages running/climbing)│
└───────────────────────┬─────────────────────────┘
                        │ HTTP / JSON
                        ▼
┌─────────────────────────────────────────────────┐
│                   FastAPI                       │
│  /api/v1/predict/running                        │
│  /api/v1/predict/climbing                       │
│  (Validation Pydantic, logique métier, routing) │
└───────────────────────┬─────────────────────────┘
                        │
              ┌─────────┴─────────┐
              ▼                   ▼
┌─────────────────┐   ┌─────────────────────┐
│  running_service│   │  climbing_service   │
│  (feature eng.  │   │  (feature eng.      │
│   + formules)   │   │   + ML)             │
└────────┬────────┘   └──────────┬──────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐   ┌─────────────────────┐
│running_model.pkl│   │climbing_model.pkl   │
│(scikit-learn)   │   │(scikit-learn)       │
└─────────────────┘   └─────────────────────┘
```

---

## Couches applicatives

### 1. Streamlit (app/)
- Point d'entrée utilisateur
- Gère les formulaires de saisie (2 modes : simple / avancé)
- Affiche les résultats et visualisations
- Consomme l'API FastAPI via `requests`
- **Ne contient pas de logique métier ni ML**

### 2. FastAPI (api/)
- Expose les endpoints de prédiction
- Valide les inputs via schémas Pydantic
- Route vers les services appropriés
- Retourne des réponses JSON structurées
- Documentation auto-générée : `http://localhost:8000/docs`

### 3. Services (api/services/)
- Contient la logique métier
- Feature engineering (normalisation, encodage, variables dérivées)
- Pour le running : intègre les formules Riegel et VDOT
- Charge les modèles `.pkl` et appelle `.predict()`
- Convertit les outputs bruts en réponses métier (ex : grade numérique → cotation française)

### 4. Modèles (models/)
- Modèles scikit-learn sérialisés en `.pkl`
- `models_metadata.json` : version, features utilisées, métriques d'évaluation, date d'entraînement
- Entraînés dans les notebooks, exportés via `joblib.dump()`

---

## Endpoints FastAPI prévus

### Running
```
POST /api/v1/predict/running
```
**Input (mode simple)** :
```json
{
  "mode": "simple",
  "age": 25,
  "gender": "M",
  "weight_kg": 70,
  "height_cm": 178,
  "resting_hr": 60,
  "max_hr": 195
}
```
**Input (mode avancé)** :
```json
{
  "mode": "advanced",
  "age": 25,
  "gender": "M",
  "recent_5k_seconds": 1320,
  "weekly_km": 40
}
```
**Output** :
```json
{
  "sport": "running",
  "mode": "simple",
  "predictions": {
    "5k_seconds": 1380,
    "10k_seconds": 2860,
    "half_marathon_seconds": 6200,
    "marathon_seconds": 13200
  },
  "vo2max_estimated": 52.3,
  "method": "VDOT + Riegel",
  "confidence": "low",
  "disclaimer": "Prédiction basée sur des formules physiologiques. Précision ±15-20% sans temps de référence."
}
```

### Escalade
```
POST /api/v1/predict/climbing
```
**Input (mode simple)** :
```json
{
  "mode": "simple",
  "age": 25,
  "weight_kg": 65,
  "height_cm": 175,
  "dead_hang_seconds": 45
}
```
**Input (mode avancé)** :
```json
{
  "mode": "advanced",
  "age": 25,
  "weight_kg": 65,
  "height_cm": 175,
  "dead_hang_seconds": 45,
  "years_climbing": 3,
  "sessions_per_week": 3,
  "max_pullups": 12
}
```
**Output** :
```json
{
  "sport": "climbing",
  "mode": "advanced",
  "predictions": {
    "grade_numeric": 42,
    "grade_french": "7a",
    "grade_range": "6c - 7b"
  },
  "confidence": "medium",
  "disclaimer": "Prédiction basée sur le dataset 8a.nu (62 000 grimpeurs). Précision ±1-2 grades."
}
```

---

## Dépendances principales

### API (api/requirements.txt)
```
fastapi>=0.110.0
uvicorn>=0.29.0
pydantic>=2.0.0
scikit-learn>=1.4.0
joblib>=1.3.0
pandas>=2.0.0
numpy>=1.26.0
```

### App Streamlit (requirements.txt global)
```
streamlit>=1.33.0
requests>=2.31.0
plotly>=5.20.0
pandas>=2.0.0
numpy>=1.26.0
```

### Notebooks (développement)
```
jupyter>=1.0.0
pandas>=2.0.0
numpy>=1.26.0
scikit-learn>=1.4.0
matplotlib>=3.8.0
seaborn>=0.13.0
statsmodels>=0.14.0
joblib>=1.3.0
```

---

## Lancement local

```bash
# 1. Lancer l'API FastAPI
python3 -m uvicorn api.main:app --reload --port 8008

# 2. Lancer l'app Streamlit (dans un autre terminal)
streamlit run app/main.py

# Documentation API disponible sur :
# http://localhost:8008/docs
```
