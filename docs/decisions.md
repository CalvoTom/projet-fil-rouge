# Architecture Decision Records (ADR)

> Chaque décision significative est consignée ici avec son contexte et sa justification.
> Format : date — décision — contexte — alternatives considérées — raison du choix.

---

## ADR-001 — Périmètre sports V1 : Running + Escalade uniquement

**Date** : 2026-04-20  
**Statut** : Accepté

**Contexte** : Le projet initial envisageait 6 sports (running, escalade, football, basket, trail, natation).

**Décision** : Limiter la V1 à Running et Escalade.

**Raisons** :
- Football et basket : données individuelles physiologiques inexistantes en open data. Les datasets publics sont collectifs (matchs, équipes). Problème mal défini pour un profil physio individuel.
- Trail : sous-ensemble du running mais les données D+ sont contextuelles et requièrent un fichier GPX. Non réalisable sans GPS.
- Natation : possible en V2 — World Aquatics a des données, mais croisement nage/distance/style complexifie le problème.
- Running et escalade : datasets de qualité disponibles, problèmes ML bien posés, variables simples suffisantes.

**Conséquences** : Natation et trail peuvent être intégrés en V2 si le temps le permet.

---

## ADR-002 — Stack UI : Streamlit (React abandonné)

**Date** : 2026-04-20  
**Statut** : Accepté

**Contexte** : L'idée initiale incluait un frontend React + API Python.

**Décision** : Remplacer React par Streamlit.

**Raisons** :
- React n'est pas dans les outils attendus par l'école (Streamlit/Dash/Panel/Bokeh/Anvil sont explicitement cités).
- React représente 3-4 semaines de développement JS/CSS/state sans valeur ajoutée pour la partie Data évaluée.
- Streamlit est natif Python, intègre matplotlib/plotly nativement, livrable en 2-3 jours.
- L'API FastAPI est conservée : Streamlit la consomme exactement comme React l'aurait fait.

**Conséquences** : Le projet reste 100% Python. L'API reste découplée et réutilisable.

---

## ADR-003 — Backend API : FastAPI

**Date** : 2026-04-20  
**Statut** : Accepté

**Contexte** : Choix entre Flask, FastAPI, ou Streamlit seul (sans API).

**Décision** : FastAPI.

**Raisons** :
- Documentation Swagger auto-générée (valorisable en soutenance comme "API production-ready").
- Validation Pydantic native des inputs/outputs.
- Séparation propre logique métier / présentation / modèles.
- Plus moderne et performant que Flask pour ce cas d'usage.
- Streamlit seul aurait couplé UI et logique ML — moins défendable architecturalement.

**Conséquences** : L'API peut être consommée par d'autres clients que Streamlit (démo possible via Swagger).

---

## ADR-004 — Dataset Running : Boston Marathon 2015-2017

**Date** : 2026-04-20  
**Statut** : Accepté

**Contexte** : Plusieurs datasets running disponibles sur Kaggle.

**Décision** : Utiliser Boston Marathon 2015-2017 (rojour/boston-results) comme dataset principal.

**Raisons** :
- ~80 000 finishers, données officielles de course.
- Contient âge, sexe, et 9 splits de temps (5k → 40k) → richesse pour la modélisation.
- Permet d'entraîner un modèle : temps 5k/10k + âge/sexe → prédiction marathon.

**Limitation connue** : Pas de poids, taille, FC. Le modèle running est donc basé sur temps de référence (mode avancé) ou formules physiologiques (mode simple). Cette limite est documentée et assumée.

**Baseline** : Formule Riegel (T₂ = T₁ × (D₂/D₁)^1.06) et tables VDOT Jack Daniels — publiées, citables, utilisées comme point de comparaison.

---

## ADR-005 — Dataset Escalade : 8a.nu Climbing Logbook

**Date** : 2026-04-20  
**Statut** : Accepté

**Contexte** : Recherche de datasets escalade avec profils physiologiques.

**Décision** : Utiliser le dataset 8a.nu (dcohen21/8anu-climbing-logbook) sur Kaggle.

**Raisons** :
- 4,1M ascensions / 62 000 grimpeurs uniques.
- Contient taille, poids, âge, années de pratique, cotation max — exactement les features nécessaires.
- Dataset académique de référence (cité UC Berkeley, Stanford).
- Format SQLite — nécessite une étape de chargement et jointure (compétence data valorisable).

**Conséquences** : La cible de prédiction est le grade max numérique (0-82), converti en cotation française pour l'affichage.

---

## ADR-006 — Approche modélisation Running : baseline déterministe + ML

**Date** : 2026-04-20  
**Statut** : Accepté

**Contexte** : Le dataset Boston Marathon ne contient pas de données physiologiques brutes (poids, FC).

**Décision** : Architecture en 2 couches pour le running.
1. **Mode simple** : formules physiologiques (Astrand pour VO2max depuis FC, VDOT pour temps prédit) — déterministe, pas de ML.
2. **Mode avancé** : modèle ML entraîné sur Boston Marathon (features : temps 5k/10k + âge/sexe → target : temps marathon).

**Raisons** :
- Présenter le ML comme un raffinement d'une baseline scientifique est plus défendable qu'un modèle "boîte noire".
- Permet de comparer baseline vs ML dans le notebook d'évaluation (valeur pédagogique forte).
- Honnête sur les limites : un débutant sans temps de référence obtiendra une estimation large (documentée).
