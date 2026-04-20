# Sources de données

> Dernière mise à jour : 2026-04-20

---

## Datasets retenus

### Running — Boston Marathon 2015-2017

| Attribut | Valeur |
|---|---|
| **Source** | Kaggle |
| **URL** | https://www.kaggle.com/datasets/rojour/boston-results |
| **Auteur** | rojour |
| **Format** | CSV |
| **Taille** | ~80 000 lignes (3 fichiers annuels) |
| **Statut** | ✅ Téléchargé — `data/raw/running/` |
| **Licence** | Publique (Kaggle) |

**Colonnes disponibles** :
- `Age`, `M/F` (sexe)
- Splits : `5K`, `10K`, `15K`, `20K`, `Half`, `25K`, `30K`, `35K`, `40K`
- `Pace`, `Official Time`, `Overall`, `Gender`, `Division`

**Colonnes manquantes** (limitation documentée) :
- Poids, taille, fréquence cardiaque, VO2max → non disponibles
- Impact : mode simple running basé sur formules physiologiques, pas sur ML pur

**Usage prévu** :
- EDA : distributions démographiques, analyse des splits, corrélations
- Modèle : temps 5k/10k + âge/sexe → prédiction temps marathon (régression)
- Baseline : comparaison avec formule Riegel

---

### Escalade — Climb Dataset (jordizar)

| Attribut | Valeur |
|---|---|
| **Source** | Kaggle |
| **URL** | https://www.kaggle.com/datasets/jordizar/climb-dataset |
| **Auteur** | jordizar |
| **Format** | CSV (3 fichiers) |
| **Taille** | 10 927 grimpeurs uniques |
| **Statut** | ✅ Téléchargé — `data/raw/climbing/` |
| **Licence** | DbCL-1.0 |

**Fichiers disponibles** :
- `climber_df.csv` : profils grimpeurs (user_id, country, sex, height, weight, age, years_cl, grades_max, grades_mean, grades_count...)
- `grades_conversion_table.csv` : mapping grade_id (0-84) ↔ cotation française (5a → 9c+)
- `routes_rated.csv` : routes cotées

**Colonnes clés pour la modélisation** :
- Features : `sex` (0/1), `height`, `weight`, `age`, `years_cl`
- Target : `grades_max` (numérique 29-77, médiane 53 ≈ 7b)

**Qualité** : 0 valeurs manquantes sur toutes les colonnes

**Biais connu** :
- Dataset issu de 8a.nu — surreprésentation des grimpeurs avancés
- grades_max médian = 53 (7b) : peu de débutants dans le dataset
- À documenter dans le notebook et mitiger par communication claire des limites

**Note** : Le dataset original 8a.nu (dcohen21, 4M ascensions, SQLite) est inaccessible via API (page supprimée). Ce dataset CSV en est une version consolidée suffisante pour le projet.

---

## Références physiologiques (non-datasets)

### Formule Riegel
- **Type** : Formule empirique de prédiction de temps de course
- **Formule** : `T₂ = T₁ × (D₂/D₁)^1.06`
- **Validité** : 3min30 → 3h50 (distances courtes à marathon)
- **Publication** : Peter Riegel, Runner's World, août 1977 ; American Scientist, 1981
- **Usage** : Baseline running mode simple et mode avancé

### Tables VDOT — Jack Daniels
- **Type** : Système empirique VO2max ↔ temps de course
- **Usage** : Convertir un temps récent (5k/10k) en VDOT, puis prédire les autres distances
- **Précision** : ±5-8% pour coureurs entraînés
- **Publication** : "Daniels' Running Formula", recherche 1970s-1980s
- **Calculateurs** : https://vdoto2.com/calculator

### Formule Åstrand-Ryhming
- **Type** : Estimation VO2max depuis FC lors d'un effort sous-maximal
- **Usage** : Mode simple running (utilisateur sans temps de référence)
- **Publication** : Journal of Applied Physiology, 1954
- **Formule homme** : `VO2max = (0.00212 × charge + 0.299) / (0.769 × FC - 48.5) × 100`
- **Formule femme** : `VO2max = (0.00193 × charge + 0.326) / (0.769 × FC - 56.1) × 100`

---

## Instructions de téléchargement

### Prérequis
```bash
pip install kaggle
# Placer kaggle.json dans ~/.kaggle/
```

### Téléchargement
```bash
# Boston Marathon
kaggle datasets download -d rojour/boston-results -p data/raw/running/

# 8a.nu Climbing Logbook
kaggle datasets download -d dcohen21/8anu-climbing-logbook -p data/raw/climbing/
```

### Décompression
```bash
cd data/raw/running && unzip boston-results.zip
cd data/raw/climbing && unzip 8anu-climbing-logbook.zip
```

> Les fichiers bruts ne sont pas versionnés dans Git (voir `.gitignore`).
> Taille estimée : Boston ~5MB, 8a.nu ~200MB.
