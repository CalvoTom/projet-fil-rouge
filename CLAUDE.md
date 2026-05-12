# CLAUDE.md — Contexte projet pour IA

> Ce fichier est le point d'entrée unique pour toute IA assistant ce projet.
> Il est maintenu à jour à chaque évolution significative.
> Dernière mise à jour : 2026-05-12

---

## 1. Présentation du projet

**Nom** : Projet fil rouge — Prédiction sportive  
**Formation** : Ynov Informatique — Bachelor 3 — Spécialité Data & IA  
**Auteur** : Romeo Bernard (rbernard2005@gmail.com)  
**Dépôt** : projet-fil-rouge  
**Statut actuel** : Phase de finalisation (documentation + polish)

### Objectif produit
Application web permettant à un utilisateur de saisir ses données physiologiques simples et d'obtenir des prédictions de performance sportive personnalisées.

### Sports couverts (V1 — livrés)
- **Running** : prédiction de temps sur 5km, 10km, semi-marathon, marathon
- **Escalade** : prédiction de niveau (cotation française falaise)
- **Cyclisme** : prédiction de vitesse moyenne selon distance
- **Natation** : prédiction d'allure (pace/100m) selon distance

---

## 2. Décisions architecturales clés

| Décision | Choix retenu | Raison |
|---|---|---|
| Framework UI | **Streamlit** | Dans les outils attendus école, rapide, natif Python/data |
| Backend API | **FastAPI** | API découplée, Swagger auto, Pydantic, réutilisable |
| Modèles | **scikit-learn (.pkl)** | Standard école, versionnable, simple à déployer |
| Frontend JS | **Abandonné** (React écarté) | Hors périmètre école, trop long à développer |
| Notebooks | **Jupyter** | Obligatoire école |
| Versioning | **Git/GitHub** | Obligatoire école |

### Stack complète
```
[Streamlit app] → HTTP → [FastAPI] → [Modèles .pkl scikit-learn]
```

---

## 3. Datasets retenus

### Running
- **Source** : Boston Marathon 2015-2017 (Kaggle — rojour/boston-results)
- **Taille** : ~80 000 finishers
- **Colonnes clés** : Âge, sexe, splits 5k/10k/15k/.../40k, temps final
- **Limitation** : Pas de poids/taille/FC → modèle basé sur temps de référence + âge/sexe
- **Baseline** : Formule Riegel (T₂ = T₁ × (D₂/D₁)^1.06) + tables VDOT Jack Daniels

### Escalade
- **Source** : jordizar/climb-dataset (Kaggle — miroir nettoyé de 8a.nu)
- **Taille** : ~10 900 grimpeurs (8 728 train / 2 182 test)
- **Colonnes clés** : Taille, poids, âge, années de pratique, cotation max (0-82)
- **Qualité** : Dataset académique de référence (cité Stanford, UC Berkeley)
- **Biais documenté** : Surreprésentation grimpeurs avancés (médiane 7b). Aucun débutant absolu.

### Cyclisme & Natation
- **Source** : vladislavboyadzhi/triathlon-results (Kaggle)
- **Taille** : ~2,6M résultats (cyclisme) / ~2,6M résultats (natation)
- **Colonnes clés** : Âge, sexe, distance, vitesse/allure
- **Usage** : Mode simple uniquement (formules physiologiques) + ML basique âge/sexe/distance

---

## 4. Modélisation — résultats réels

### Running ✅
- **Problème** : Régression
- **Mode simple** : Formule Uth (FC → VO2max) + VDOT Jack Daniels + Riegel (déterministe)
- **Mode avancé** : ML avec temps récent 5k ou 10k
- **Modèle** : Gradient Boosting
- **Features** : Age, gender, 5K_sec, speed_5k
- **Target** : Temps marathon (secondes) — extrapolé aux autres distances via Riegel
- **Métriques** : MAE 13,9 min | MAPE 5,8% | R² 0,79
- **Dataset** : Boston Marathon 2015-2017

### Escalade ✅
- **Problème** : Classification (5 niveaux)
- **Architecture** :
  - `years_cl = 0` → Mode POTENTIEL : règles physiologiques (dead hang, BMI, tractions), pas de ML
  - `years_cl ≥ 1` → Mode ML : Gradient Boosting
- **Features ML** : sex, height, weight, bmi, age, years_cl
- **Target** : level_class (0-4) → cotation française
- **Métriques** : Accuracy 39,7% | Within ±1 classe : 80,1%
- **Dataset** : jordizar/climb-dataset (10 910 grimpeurs)

### Cyclisme ✅
- **Problème** : Régression
- **Mode simple** : Formule physiologique (poids requis selon puissance)
- **Mode avancé** : ML
- **Modèle** : Gradient Boosting
- **Features** : age, gender, dist_km
- **Target** : speed_kmh
- **Métriques** : MAE 3,14 km/h | MAPE 11,0% | R² 0,12
- **Dataset** : vladislavboyadzhi/triathlon-results (2,6M résultats)

### Natation ✅
- **Problème** : Régression
- **Mode simple** : Formule physiologique (poids requis)
- **Mode avancé** : ML
- **Modèle** : Gradient Boosting
- **Features** : age, gender, dist_m
- **Target** : pace_per_100m (secondes)
- **Métriques** : MAE 19,73 s/100m | MAPE 16,7% | R² 0,06
- **Dataset** : vladislavboyadzhi/triathlon-results (2,6M résultats)

---

## 5. Structure du dépôt

```
projet-fil-rouge/
├── CLAUDE.md                   ← Ce fichier (point d'entrée IA)
├── README.md                   ← Installation et présentation
├── .gitignore
├── requirements.txt            ← Dépendances globales
│
├── data/
│   ├── raw/                    ← Données brutes (non versionnées si >50MB)
│   ├── processed/              ← CSV nettoyés
│   └── external/               ← Tables VDOT, mapping cotations
│
├── notebooks/
│   ├── 01_eda_running.ipynb
│   ├── 02_eda_climbing.ipynb
│   ├── 03_model_running.ipynb
│   ├── 04_model_climbing.ipynb
│   ├── 05_eda_cycling.ipynb
│   ├── 06_eda_swimming.ipynb
│   ├── 07_model_cycling.ipynb
│   └── 08_model_swimming.ipynb
│
├── models/
│   ├── running_model.pkl
│   ├── running_metadata.json
│   ├── climbing_model.pkl
│   ├── climbing_grade_map.pkl
│   ├── climbing_level_config.pkl
│   ├── climbing_metadata.json
│   ├── cycling_model.pkl
│   ├── cycling_metadata.json
│   ├── swimming_model.pkl
│   └── swimming_metadata.json
│
├── api/
│   ├── main.py
│   ├── routers/
│   │   ├── running.py
│   │   ├── climbing.py
│   │   ├── cycling.py
│   │   └── swimming.py
│   ├── schemas/
│   │   ├── running.py
│   │   ├── climbing.py
│   │   ├── cycling.py
│   │   └── swimming.py
│   ├── services/
│   │   ├── running_service.py
│   │   ├── climbing_service.py
│   │   ├── cycling_service.py
│   │   └── swimming_service.py
│   └── requirements.txt
│
├── app/
│   ├── main.py                 ← Streamlit entry point
│   └── pages/
│       ├── running.py
│       ├── climbing.py
│       ├── cycling.py
│       └── swimming.py
│
└── docs/
    ├── architecture.md
    ├── data_sources.md
    ├── decisions.md            ← ADR (Architecture Decision Records)
    └── roadmap.md
```

---

## 6. État d'avancement

| Phase | Statut | Notes |
|---|---|---|
| Cadrage projet | ✅ Terminé | 4 sports retenus, stack décidée |
| Setup repo & docs | ✅ Terminé | Structure complète |
| Téléchargement datasets | ✅ Terminé | Boston Marathon + Climb Dataset + Triathlon Results |
| EDA Running | ✅ Terminé | notebooks/01_eda_running.ipynb |
| EDA Escalade | ✅ Terminé | notebooks/02_eda_climbing.ipynb |
| EDA Cyclisme | ✅ Terminé | notebooks/05_eda_cycling.ipynb |
| EDA Natation | ✅ Terminé | notebooks/06_eda_swimming.ipynb |
| Modèle Running | ✅ Terminé | GBM — MAE 13,9 min, R² 0,79 |
| Modèle Escalade | ✅ Terminé | GBM classif — Within ±1 classe : 80,1% |
| Modèle Cyclisme | ✅ Terminé | GBM — MAE 3,14 km/h |
| Modèle Natation | ✅ Terminé | GBM — MAE 19,7 s/100m |
| FastAPI | ✅ Terminé | 4 routers, 7 endpoints, Swagger dispo sur :8008/docs |
| Streamlit | ✅ Terminé | 4 pages, mode simple + avancé |
| Documentation finale | ⬜ À faire | README à jour, docs/ à compléter |

---

## 7. Contraintes à respecter

- Python obligatoire pour tout le traitement data et le backend
- Jupyter Notebook pour retracer la démarche (obligatoire école)
- Librairies attendues : pandas, numpy, scikit-learn, statsmodels, matplotlib, seaborn
- Application déployable localement (pas de cloud requis)
- Documentation technique complète attendue

---

## 8. Conventions de travail

- Toute décision architecturale significative → ajoutée dans `docs/decisions.md`
- Tout changement de périmètre → mis à jour dans ce fichier (section 6)
- Données brutes >50MB → non versionnées, listées dans `data/raw/.gitkeep` avec source URL
- Modèles exportés → accompagnés de `models_metadata.json` à jour
- Chaque notebook commence par une cellule markdown expliquant son objectif

---

## 9. Pour démarrer sur ce projet (onboarding IA)

1. Lire ce fichier en entier
2. Lire `docs/decisions.md` pour comprendre les choix et leur contexte
3. Lire `docs/roadmap.md` pour connaître l'étape courante
4. Consulter `docs/data_sources.md` pour l'état des données disponibles
5. Vérifier la section 6 (état d'avancement) pour savoir où en est le projet
