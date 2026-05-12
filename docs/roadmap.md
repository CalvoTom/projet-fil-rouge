# Roadmap — Projet fil rouge

> Dernière mise à jour : 2026-05-12

---

## État global

**Phase courante** : Finalisation — documentation technique + polish  
**Prochaine étape** : Compléter `docs/`, vérifier le notebook `05_evaluation_recap.ipynb`, préparer la soutenance

---

## Planning détaillé

| Semaine | Phase | Objectifs | Livrables | Statut |
|---|---|---|---|---|
| 1 | Setup & Data | Init repo, structure dossiers, téléchargement datasets, audit qualité | Repo structuré, données brutes présentes, `.gitignore`, `README` | ✅ Terminé |
| 2 | EDA Running | Exploration Boston Marathon : distributions, corrélations, outliers, splits | `notebooks/01_eda_running.ipynb` | ✅ Terminé |
| 3 | EDA Escalade | Exploration climb-dataset : distributions, corrélations | `notebooks/02_eda_climbing.ipynb` | ✅ Terminé |
| 4 | Feature Eng. Running | Nettoyage, variables dérivées, baseline Riegel/VDOT codée | Features prêtes, baseline validée | ✅ Terminé |
| 5 | Modèle Running | Entraînement GBM, évaluation, export | `notebooks/03_model_running.ipynb`, `models/running_model.pkl` | ✅ Terminé |
| 6 | Modèle Escalade | Feature engineering, entraînement, évaluation, export | `notebooks/04_model_climbing.ipynb`, `models/climbing_model.pkl` | ✅ Terminé |
| 6b | EDA + Modèles Cyclisme/Natation | Extension périmètre — 2 sports supplémentaires | `notebooks/05-08_*.ipynb`, `models/cycling_model.pkl`, `models/swimming_model.pkl` | ✅ Terminé |
| 7 | Évaluation recap | Comparaison baseline vs ML, interprétation, visualisations finales | `notebooks/05_evaluation_recap.ipynb` | ⬜ À faire |
| 8 | FastAPI | Endpoints 4 sports, schémas Pydantic, tests | API fonctionnelle testable via Swagger | ✅ Terminé |
| 9 | Streamlit | Interface 4 sports (mode simple/avancé), visualisations résultats | App déployable localement | ✅ Terminé |
| 10 | Finalisation | Documentation complète, README, répétition soutenance | Dépôt final livrable | 🔄 En cours |

---

## Décisions de périmètre

- **V1 livrée** : Running + Escalade + Cyclisme + Natation (4 sports)
- **Écarté en cours de projet** : Tennis (module créé puis supprimé — données insuffisantes)
- **Écarté définitivement** : Football, Basket (problème data mal posé pour profil individuel)

---

## Risques identifiés

| Risque | Probabilité | Impact | Mitigation |
|---|---|---|---|
| R² faible cyclisme (0,12) et natation (0,06) | Réalisé | Moyen | Documenté dans les métadonnées — mode simple (formules physio) mis en avant |
| Dataset 8a.nu : biais grimpeurs avancés | Réalisé | Moyen | Stratification appliquée, biais documenté dans les métadonnées |
| Streamlit trop limité pour les visualisations souhaitées | Non réalisé | — | Plotly natif utilisé — aucun problème |
| Temps insuffisant pour documentation finale | Actif | Moyen | docs/ à compléter en priorité |
