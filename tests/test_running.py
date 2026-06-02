from unittest.mock import patch
from tests.conftest import MOCK_RUNNING_ADVANCED

# ---------------------------------------------------------------------------
# Mode simple (formules pures — pas de modèle ML)
# ---------------------------------------------------------------------------

def test_simple_valid_male(client):
    r = client.post("/api/v1/running/predict/simple", json={
        "age": 30, "gender": 0, "resting_hr": 60,
    })
    assert r.status_code == 200


def test_simple_valid_female(client):
    r = client.post("/api/v1/running/predict/simple", json={
        "age": 25, "gender": 1, "resting_hr": 65,
    })
    assert r.status_code == 200


def test_simple_response_structure(client):
    r = client.post("/api/v1/running/predict/simple", json={
        "age": 35, "gender": 0, "resting_hr": 55,
    })
    data = r.json()
    assert data["sport"] == "running"
    assert data["mode"] == "simple"
    assert "level_label" in data
    assert "vo2max_estimated" in data
    assert "confidence" in data
    assert data["confidence"] in ("low", "medium", "high")


def test_simple_predictions_count(client):
    r = client.post("/api/v1/running/predict/simple", json={
        "age": 40, "gender": 0, "resting_hr": 70,
    })
    predictions = r.json()["predictions"]
    assert len(predictions) == 4
    distances = [p["distance"] for p in predictions]
    assert "5km" in distances
    assert "Marathon" in distances


def test_simple_prediction_times_coherent(client):
    r = client.post("/api/v1/running/predict/simple", json={
        "age": 30, "gender": 0, "resting_hr": 60,
    })
    preds = {p["distance"]: p["seconds"] for p in r.json()["predictions"]}
    assert preds["5km"] < preds["10km"] < preds["Semi-marathon"] < preds["Marathon"]


def test_simple_with_optional_fields(client):
    r = client.post("/api/v1/running/predict/simple", json={
        "age": 30, "gender": 0, "resting_hr": 60,
        "max_hr": 185, "weight_kg": 75.0,
    })
    assert r.status_code == 200


def test_simple_female_slower_than_male(client):
    male = client.post("/api/v1/running/predict/simple", json={
        "age": 30, "gender": 0, "resting_hr": 60,
    }).json()
    female = client.post("/api/v1/running/predict/simple", json={
        "age": 30, "gender": 1, "resting_hr": 60,
    }).json()
    male_marathon = next(p["seconds"] for p in male["predictions"] if p["distance"] == "Marathon")
    female_marathon = next(p["seconds"] for p in female["predictions"] if p["distance"] == "Marathon")
    assert female_marathon > male_marathon


# --- Validation : âge ---

def test_simple_age_too_young(client):
    r = client.post("/api/v1/running/predict/simple", json={
        "age": 10, "gender": 0, "resting_hr": 60,
    })
    assert r.status_code == 422


def test_simple_age_too_old(client):
    r = client.post("/api/v1/running/predict/simple", json={
        "age": 90, "gender": 0, "resting_hr": 60,
    })
    assert r.status_code == 422


def test_simple_age_boundary_min(client):
    r = client.post("/api/v1/running/predict/simple", json={
        "age": 15, "gender": 0, "resting_hr": 60,
    })
    assert r.status_code == 200


def test_simple_age_boundary_max(client):
    r = client.post("/api/v1/running/predict/simple", json={
        "age": 85, "gender": 0, "resting_hr": 60,
    })
    assert r.status_code == 200


# --- Validation : FC repos ---

def test_simple_resting_hr_too_low(client):
    r = client.post("/api/v1/running/predict/simple", json={
        "age": 30, "gender": 0, "resting_hr": 20,
    })
    assert r.status_code == 422


def test_simple_resting_hr_too_high(client):
    r = client.post("/api/v1/running/predict/simple", json={
        "age": 30, "gender": 0, "resting_hr": 110,
    })
    assert r.status_code == 422


# --- Validation : genre ---

def test_simple_invalid_gender(client):
    r = client.post("/api/v1/running/predict/simple", json={
        "age": 30, "gender": 2, "resting_hr": 60,
    })
    assert r.status_code == 422


# ---------------------------------------------------------------------------
# Mode avancé (modèle ML — mocké)
# ---------------------------------------------------------------------------

def test_advanced_valid_with_5k(client):
    with patch("api.services.running_service.predict_advanced", return_value=MOCK_RUNNING_ADVANCED):
        r = client.post("/api/v1/running/predict/advanced", json={
            "age": 28, "gender": 0, "recent_5k_seconds": 1200,
        })
    assert r.status_code == 200


def test_advanced_valid_with_10k(client):
    with patch("api.services.running_service.predict_advanced", return_value=MOCK_RUNNING_ADVANCED):
        r = client.post("/api/v1/running/predict/advanced", json={
            "age": 28, "gender": 0, "recent_10k_seconds": 2500,
        })
    assert r.status_code == 200


def test_advanced_valid_with_both_times(client):
    with patch("api.services.running_service.predict_advanced", return_value=MOCK_RUNNING_ADVANCED):
        r = client.post("/api/v1/running/predict/advanced", json={
            "age": 28, "gender": 0,
            "recent_5k_seconds": 1200,
            "recent_10k_seconds": 2500,
        })
    assert r.status_code == 200


def test_advanced_no_times_returns_422(client):
    r = client.post("/api/v1/running/predict/advanced", json={
        "age": 28, "gender": 0,
    })
    assert r.status_code == 422


def test_advanced_5k_too_fast(client):
    r = client.post("/api/v1/running/predict/advanced", json={
        "age": 28, "gender": 0, "recent_5k_seconds": 500,
    })
    assert r.status_code == 422


def test_advanced_5k_too_slow(client):
    r = client.post("/api/v1/running/predict/advanced", json={
        "age": 28, "gender": 0, "recent_5k_seconds": 8000,
    })
    assert r.status_code == 422


def test_advanced_response_structure(client):
    with patch("api.services.running_service.predict_advanced", return_value=MOCK_RUNNING_ADVANCED):
        r = client.post("/api/v1/running/predict/advanced", json={
            "age": 28, "gender": 0, "recent_5k_seconds": 1200,
        })
    data = r.json()
    assert data["sport"] == "running"
    assert data["mode"] == "advanced"
    assert data["confidence"] == "high"
    assert len(data["predictions"]) == 4
    assert data["disclaimer"] is None


def test_advanced_formatted_time_present(client):
    with patch("api.services.running_service.predict_advanced", return_value=MOCK_RUNNING_ADVANCED):
        r = client.post("/api/v1/running/predict/advanced", json={
            "age": 28, "gender": 0, "recent_5k_seconds": 1200,
        })
    for pred in r.json()["predictions"]:
        assert "formatted" in pred
        assert "seconds" in pred
        assert pred["seconds"] > 0
