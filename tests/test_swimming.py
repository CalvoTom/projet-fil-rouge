from unittest.mock import patch
from tests.conftest import MOCK_SWIMMING_ADVANCED

BASE_SIMPLE = {
    "age": 25, "gender": 0,
    "weight_kg": 72.0, "height_cm": 175.0,
}

BASE_ADVANCED = {
    "age": 25, "gender": 0,
    "ref_distance_m": 1500,
    "ref_time_seconds": 1500,
}

# ---------------------------------------------------------------------------
# Mode simple (formules pures — pas de modèle ML)
# ---------------------------------------------------------------------------

def test_simple_valid_male(client):
    r = client.post("/api/v1/swimming/predict/simple", json=BASE_SIMPLE)
    assert r.status_code == 200


def test_simple_valid_female(client):
    r = client.post("/api/v1/swimming/predict/simple", json={**BASE_SIMPLE, "gender": 1})
    assert r.status_code == 200


def test_simple_without_height(client):
    payload = {"age": 25, "gender": 0, "weight_kg": 72.0}
    r = client.post("/api/v1/swimming/predict/simple", json=payload)
    assert r.status_code == 200


def test_simple_response_structure(client):
    r = client.post("/api/v1/swimming/predict/simple", json=BASE_SIMPLE)
    data = r.json()
    assert data["sport"] == "swimming"
    assert data["mode"] == "simple"
    assert "level_label" in data
    assert "predictions" in data


def test_simple_predictions_have_pace(client):
    r = client.post("/api/v1/swimming/predict/simple", json=BASE_SIMPLE)
    for pred in r.json()["predictions"]:
        assert "pace_per_100m" in pred
        assert "/100m" in pred["pace_per_100m"]


def test_simple_predictions_coherent(client):
    r = client.post("/api/v1/swimming/predict/simple", json=BASE_SIMPLE)
    preds = {p["distance"]: p["seconds"] for p in r.json()["predictions"]}
    times = sorted(preds.values())
    assert times == sorted(times)


# --- Validation ---

def test_simple_age_too_young(client):
    r = client.post("/api/v1/swimming/predict/simple", json={**BASE_SIMPLE, "age": 5})
    assert r.status_code == 422


def test_simple_age_too_old(client):
    r = client.post("/api/v1/swimming/predict/simple", json={**BASE_SIMPLE, "age": 90})
    assert r.status_code == 422


def test_simple_age_boundary_min(client):
    r = client.post("/api/v1/swimming/predict/simple", json={**BASE_SIMPLE, "age": 10})
    assert r.status_code == 200


def test_simple_invalid_gender(client):
    r = client.post("/api/v1/swimming/predict/simple", json={**BASE_SIMPLE, "gender": 3})
    assert r.status_code == 422


def test_simple_weight_too_light(client):
    r = client.post("/api/v1/swimming/predict/simple", json={**BASE_SIMPLE, "weight_kg": 20.0})
    assert r.status_code == 422


# ---------------------------------------------------------------------------
# Mode avancé (modèle ML — mocké)
# ---------------------------------------------------------------------------

def test_advanced_valid(client):
    with patch("api.services.swimming_service.predict_advanced", return_value=MOCK_SWIMMING_ADVANCED):
        r = client.post("/api/v1/swimming/predict/advanced", json=BASE_ADVANCED)
    assert r.status_code == 200


def test_advanced_response_structure(client):
    with patch("api.services.swimming_service.predict_advanced", return_value=MOCK_SWIMMING_ADVANCED):
        r = client.post("/api/v1/swimming/predict/advanced", json=BASE_ADVANCED)
    data = r.json()
    assert data["sport"] == "swimming"
    assert data["mode"] == "advanced"
    assert data["confidence"] == "high"
    for pred in data["predictions"]:
        assert "pace_per_100m" in pred


def test_advanced_distance_too_short(client):
    r = client.post("/api/v1/swimming/predict/advanced", json={**BASE_ADVANCED, "ref_distance_m": 50})
    assert r.status_code == 422


def test_advanced_distance_too_long(client):
    r = client.post("/api/v1/swimming/predict/advanced", json={**BASE_ADVANCED, "ref_distance_m": 6000})
    assert r.status_code == 422


def test_advanced_time_too_short(client):
    r = client.post("/api/v1/swimming/predict/advanced", json={**BASE_ADVANCED, "ref_time_seconds": 10})
    assert r.status_code == 422


def test_advanced_time_too_long(client):
    r = client.post("/api/v1/swimming/predict/advanced", json={**BASE_ADVANCED, "ref_time_seconds": 8000})
    assert r.status_code == 422
