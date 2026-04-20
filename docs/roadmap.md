# Roadmap — Projet fil rouge

> Dernière mise à jour : 2026-04-20

---

## État global

**Phase courante** : Semaine 1 — Setup & acquisition données  
**Prochaine étape** : Télécharger les datasets Kaggle et lancer l'EDA Running

---

## Planning détaillé

| Semaine | Phase | Objectifs | Livrables | Statut |
|---|---|---|---|---|
| 1 | Setup & Data | Init repo, structure dossiers, téléchargement datasets, audit qualité | Repo structuré, données brutes présentes, `.gitignore`, `README` | 🔄 En cours |
| 2 | EDA Running | Exploration Boston Marathon : distributions, corrélations, outliers, splits | `notebooks/01_eda_running.ipynb` | ⬜ |
| 3 | EDA Escalade | Exploration 8a.nu : chargement SQLite, jointures, distributions, corrélations | `notebooks/02_eda_climbing.ipynb` | ⬜ |
| 4 | Feature Eng. Running | Nettoyage, variables dérivées, baseline Riegel/VDOT codée | Features prêtes, baseline validée | ⬜ |
| 5 | Modèle Running | Entraînement Random Forest/GBM, évaluation, export | `notebooks/03_model_running.ipynb`, `models/running_model.pkl` | ⬜ |
| 6 | Modèle Escalade | Feature engineering, entraînement, évaluation, export | `notebooks/04_model_climbing.ipynb`, `models/climbing_model.pkl` | ⬜ |
| 7 | Évaluation recap | Comparaison baseline vs ML, interprétation, visualisations finales | `notebooks/05_evaluation_recap.ipynb` | ⬜ |
| 8 | FastAPI | Endpoints `/predict/running` et `/predict/climbing`, schémas Pydantic, tests | API fonctionnelle testable via Swagger | ⬜ |
| 9 | Streamlit | Interface 2 modes (simple/avancé), visualisations résultats, intégration API | App déployable localement | ⬜ |
| 10 | Finalisation | Documentation complète, README, répétition soutenance | Dépôt final livrable | ⬜ |

---

## Décisions de périmètre

- **V1** : Running + Escalade
- **V2 potentielle** : Natation, Trail (si temps disponible après semaine 9)
- **Écarté définitivement** : Football, Basket (problème data mal posé pour profil individuel)

---

## Risques identifiés

| Risque | Probabilité | Impact | Mitigation |
|---|---|---|---|
| Dataset 8a.nu trop complexe à charger (SQLite) | Faible | Moyen | Fallback : jordizar/climb-dataset (CSV pré-nettoyé) |
| Boston Marathon insuffisant pour mode simple running | Moyen | Moyen | Mode simple = formules Astrand/VDOT (déterministe, pas ML) |
| Streamlit trop limité pour les visualisations souhaitées | Faible | Faible | Plotly natif dans Streamlit — très capable |
| Temps insuffisant pour Streamlit + FastAPI | Moyen | Faible | FastAPI peut être simplifié (services appelés directement par Streamlit) |
| Modèle escalade : biais dataset (surreprésentation grimpeurs avancés sur 8a.nu) | Moyen | Moyen | Documenter le biais, stratifier l'échantillon d'entraînement |
