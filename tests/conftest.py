import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def client():
    from api.main import app
    return TestClient(app)


MOCK_RUNNING_SIMPLE = {
    "mode": "simple",
    "level_label": "Intermédiaire",
    "predictions": [
        {"distance": "5km", "seconds": 1500, "formatted": "25m00s"},
        {"distance": "10km", "seconds": 3100, "formatted": "51m40s"},
        {"distance": "Semi-marathon", "seconds": 7000, "formatted": "1h56m40s"},
        {"distance": "Marathon", "seconds": 14500, "formatted": "4h01m40s"},
    ],
    "vo2max_estimated": 42.5,
    "method": "Formule Uth (FC repos→VO2max) + VDOT Jack Daniels + Riegel",
    "confidence": "low",
    "disclaimer": "Prédiction indicative.",
}

MOCK_RUNNING_ADVANCED = {
    "mode": "advanced",
    "level_label": "Expert",
    "predictions": [
        {"distance": "5km", "seconds": 1050, "formatted": "17m30s"},
        {"distance": "10km", "seconds": 2180, "formatted": "36m20s"},
        {"distance": "Semi-marathon", "seconds": 4900, "formatted": "1h21m40s"},
        {"distance": "Marathon", "seconds": 10200, "formatted": "2h50m00s"},
    ],
    "vo2max_estimated": 60.0,
    "method": "Gradient Boosting (Boston Marathon 2015-2017) + Riegel",
    "confidence": "high",
    "disclaimer": None,
}

MOCK_CLIMBING = {
    "mode_used": "ml",
    "level_class": 2,
    "level_label": "Confirmé",
    "grade_range": "6a → 7a",
    "confidence": "high",
    "probabilities": {
        "Débutant": 0.05,
        "Intermédiaire": 0.15,
        "Confirmé": 0.60,
        "Expert": 0.20,
    },
    "disclaimer": None,
}

MOCK_CLIMBING_POTENTIAL = {
    "mode_used": "potential",
    "level_class": 1,
    "level_label": "Intermédiaire",
    "grade_range": "5c → 6b",
    "confidence": "low",
    "probabilities": None,
    "disclaimer": "Estimation basée sur votre profil physique uniquement.",
}

MOCK_CYCLING_ADVANCED = {
    "mode": "advanced",
    "level_label": "Intermédiaire",
    "predictions": [
        {"distance": "20km", "seconds": 2400, "formatted": "40m00s", "speed_kmh": 30.0},
        {"distance": "40km", "seconds": 4900, "formatted": "1h21m40s", "speed_kmh": 29.4},
        {"distance": "100km", "seconds": 12600, "formatted": "3h30m00s", "speed_kmh": 28.6},
    ],
    "method": "Riegel + correction effort",
    "confidence": "high",
    "disclaimer": None,
}

MOCK_SWIMMING_ADVANCED = {
    "mode": "advanced",
    "level_label": "Intermédiaire",
    "predictions": [
        {"distance": "400m", "seconds": 480, "formatted": "8m00s", "pace_per_100m": "2:00/100m"},
        {"distance": "1500m", "seconds": 1900, "formatted": "31m40s", "pace_per_100m": "2:07/100m"},
        {"distance": "3800m", "seconds": 5200, "formatted": "1h26m40s", "pace_per_100m": "2:17/100m"},
    ],
    "method": "Riegel",
    "confidence": "high",
    "disclaimer": None,
}
