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
