# CLAUDE.md — Contexte projet pour IA

> Ce fichier est le point d'entrée unique pour toute IA assistant ce projet.
> Il est maintenu à jour à chaque évolution significative.
> Dernière mise à jour : 2026-04-20

---

## 1. Présentation du projet

**Nom** : Projet fil rouge — Prédiction sportive  
**Formation** : Ynov Informatique — Bachelor 3 — Spécialité Data & IA  
**Auteur** : Romeo Bernard (rbernard2005@gmail.com)  
**Dépôt** : projet-fil-rouge  
**Statut actuel** : Phase de mise en place (semaine 1)

### Objectif produit
Application web permettant à un utilisateur de saisir ses données physiologiques simples et d'obtenir des prédictions de performance sportive personnalisées.

### Sports retenus (V1)
- **Running** : prédiction de temps sur 5km, 10km, semi-marathon, marathon
- **Escalade** : prédiction de niveau (cotation française falaise)

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
- **Source** : 8a.nu Climbing Logbook (Kaggle — dcohen21/8anu-climbing-logbook)
- **Taille** : 4,1M ascensions / 62 000 grimpeurs uniques
- **Colonnes clés** : Taille, poids, âge, années de pratique, cotation max (0-82)
- **Format** : SQLite (4 tables : users, ascents, grades, methods)
- **Qualité** : Dataset académique de référence (cité Stanford, UC Berkeley)

---

## 4. Modélisation prévue

### Running
- **Problème** : Régression
- **Features mode simple** : Âge, sexe, FC repos (→ VO2max estimé via Astrand → VDOT)
- **Features mode avancé** : + Temps récent 5k ou 10k, volume hebdo
- **Target** : Temps marathon (secondes) — extrapolable aux autres distances via Riegel
- **Modèle** : Random Forest Regressor / Gradient Boosting
- **Métriques** : MAE (s), MAPE (%), R²
- **Baseline à battre** : Formule Riegel

### Escalade
- **Problème** : Régression (grade numérique 0-82)
- **Features mode simple** : Poids, taille, âge, dead hang (secondes)
- **Features mode avancé** : + Années pratique, fréquence hebdo, tractions max
- **Target** : Grade max (numérique → converti en cotation française)
- **Modèle** : Random Forest Regressor
- **Métriques** : MAE en grades, Accuracy ±1 grade
- **Baseline à battre** : Moyenne par tranche d'âge/poids

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
│   └── 05_evaluation_recap.ipynb
│
├── models/
│   ├── running_model.pkl
│   ├── climbing_model.pkl
│   └── models_metadata.json    ← Version, features, métriques, date
│
├── api/
│   ├── main.py
│   ├── routers/
│   │   ├── running.py
│   │   └── climbing.py
│   ├── schemas/
│   │   ├── running.py          ← Pydantic input/output
│   │   └── climbing.py
│   ├── services/
│   │   ├── running_service.py
│   │   └── climbing_service.py
│   └── requirements.txt
│
├── app/
│   ├── main.py                 ← Streamlit entry point
│   ├── pages/
│   │   ├── running.py
│   │   └── climbing.py
│   └── components/
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
| Cadrage projet | ✅ Terminé | Sports, stack, datasets décidés |
| Setup repo & docs | ✅ En cours | Structure créée |
| Téléchargement datasets | ⬜ À faire | Kaggle : boston-results + 8anu-climbing-logbook |
| EDA Running | ⬜ À faire | |
| EDA Escalade | ⬜ À faire | |
| Modèle Running | ⬜ À faire | |
| Modèle Escalade | ⬜ À faire | |
| FastAPI | ⬜ À faire | |
| Streamlit | ⬜ À faire | |
| Documentation finale | ⬜ À faire | |

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
