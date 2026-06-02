from unittest.mock import patch
from tests.conftest import MOCK_CYCLING_ADVANCED

BASE_SIMPLE = {
    "age": 30, "gender": 0,
    "weight_kg": 75.0, "height_cm": 178.0,
}

BASE_ADVANCED = {
    "age": 30, "gender": 0,
    "ref_distance_km": 40.0,
    "ref_time_seconds": 4800,
}

# ---------------------------------------------------------------------------
# Mode simple (formules pures — pas de modèle ML)
# ---------------------------------------------------------------------------

def test_simple_valid_male(client):
    r = client.post("/api/v1/cycling/predict/simple", json=BASE_SIMPLE)
    assert r.status_code == 200


def test_simple_valid_female(client):
    r = client.post("/api/v1/cycling/predict/simple", json={**BASE_SIMPLE, "gender": 1})
    assert r.status_code == 200


def test_simple_without_height(client):
    payload = {"age": 30, "gender": 0, "weight_kg": 75.0}
    r = client.post("/api/v1/cycling/predict/simple", json=payload)
    assert r.status_code == 200


def test_simple_response_structure(client):
    r = client.post("/api/v1/cycling/predict/simple", json=BASE_SIMPLE)
    data = r.json()
    assert data["sport"] == "cycling"
    assert data["mode"] == "simple"
    assert "level_label" in data
    assert "predictions" in data
    assert data["confidence"] in ("low", "medium", "high")


def test_simple_predictions_have_speed(client):
    r = client.post("/api/v1/cycling/predict/simple", json=BASE_SIMPLE)
    for pred in r.json()["predictions"]:
        assert "speed_kmh" in pred
        assert pred["speed_kmh"] > 0


def test_simple_predictions_coherent(client):
    r = client.post("/api/v1/cycling/predict/simple", json=BASE_SIMPLE)
    preds = {p["distance"]: p["seconds"] for p in r.json()["predictions"]}
    times = sorted(preds.values())
    assert times == sorted(times)


# --- Validation ---

def test_simple_age_too_young(client):
    r = client.post("/api/v1/cycling/predict/simple", json={**BASE_SIMPLE, "age": 10})
    assert r.status_code == 422


def test_simple_age_too_old(client):
    r = client.post("/api/v1/cycling/predict/simple", json={**BASE_SIMPLE, "age": 90})
    assert r.status_code == 422


def test_simple_invalid_gender(client):
    r = client.post("/api/v1/cycling/predict/simple", json={**BASE_SIMPLE, "gender": 3})
    assert r.status_code == 422


def test_simple_weight_too_light(client):
    r = client.post("/api/v1/cycling/predict/simple", json={**BASE_SIMPLE, "weight_kg": 20.0})
    assert r.status_code == 422


# ---------------------------------------------------------------------------
# Mode avancé (modèle ML — mocké)
# ---------------------------------------------------------------------------

def test_advanced_valid(client):
    with patch("api.services.cycling_service.predict_advanced", return_value=MOCK_CYCLING_ADVANCED):
        r = client.post("/api/v1/cycling/predict/advanced", json=BASE_ADVANCED)
    assert r.status_code == 200


def test_advanced_response_structure(client):
    with patch("api.services.cycling_service.predict_advanced", return_value=MOCK_CYCLING_ADVANCED):
        r = client.post("/api/v1/cycling/predict/advanced", json=BASE_ADVANCED)
    data = r.json()
    assert data["sport"] == "cycling"
    assert data["mode"] == "advanced"
    assert data["confidence"] == "high"
    for pred in data["predictions"]:
        assert "speed_kmh" in pred


def test_advanced_distance_too_short(client):
    r = client.post("/api/v1/cycling/predict/advanced", json={**BASE_ADVANCED, "ref_distance_km": 2.0})
    assert r.status_code == 422


def test_advanced_distance_too_long(client):
    r = client.post("/api/v1/cycling/predict/advanced", json={**BASE_ADVANCED, "ref_distance_km": 300.0})
    assert r.status_code == 422


def test_advanced_time_too_short(client):
    r = client.post("/api/v1/cycling/predict/advanced", json={**BASE_ADVANCED, "ref_time_seconds": 100})
    assert r.status_code == 422


def test_advanced_time_too_long(client):
    r = client.post("/api/v1/cycling/predict/advanced", json={**BASE_ADVANCED, "ref_time_seconds": 40000})
    assert r.status_code == 422
