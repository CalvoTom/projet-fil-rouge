from unittest.mock import patch
from tests.conftest import MOCK_CLIMBING, MOCK_CLIMBING_POTENTIAL

BASE = {
    "age": 25, "gender": 0,
    "height_cm": 175.0, "weight_kg": 70.0,
    "years_climbing": 3.0,
}

# ---------------------------------------------------------------------------
# Réponses valides (mocké — modèle ML requis)
# ---------------------------------------------------------------------------

def test_predict_experienced_climber(client):
    with patch("api.services.climbing_service.predict", return_value=MOCK_CLIMBING):
        r = client.post("/api/v1/climbing/predict", json=BASE)
    assert r.status_code == 200


def test_predict_beginner_potential_mode(client):
    payload = {**BASE, "years_climbing": 0}
    with patch("api.services.climbing_service.predict", return_value=MOCK_CLIMBING_POTENTIAL):
        r = client.post("/api/v1/climbing/predict", json=payload)
    assert r.status_code == 200


def test_predict_response_structure_ml(client):
    with patch("api.services.climbing_service.predict", return_value=MOCK_CLIMBING):
        r = client.post("/api/v1/climbing/predict", json=BASE)
    data = r.json()
    assert data["sport"] == "climbing"
    assert data["mode_used"] == "ml"
    assert "level_class" in data
    assert "level_label" in data
    assert "grade_range" in data
    assert data["confidence"] in ("low", "medium", "high")
    assert isinstance(data["probabilities"], dict)


def test_predict_response_structure_potential(client):
    payload = {**BASE, "years_climbing": 0}
    with patch("api.services.climbing_service.predict", return_value=MOCK_CLIMBING_POTENTIAL):
        r = client.post("/api/v1/climbing/predict", json=payload)
    data = r.json()
    assert data["mode_used"] == "potential"
    assert data["probabilities"] is None
    assert data["confidence"] == "low"
    assert data["disclaimer"] is not None


def test_predict_with_dead_hang(client):
    payload = {**BASE, "dead_hang_seconds": 45}
    with patch("api.services.climbing_service.predict", return_value=MOCK_CLIMBING):
        r = client.post("/api/v1/climbing/predict", json=payload)
    assert r.status_code == 200


def test_predict_with_pullups(client):
    payload = {**BASE, "max_pullups": 12}
    with patch("api.services.climbing_service.predict", return_value=MOCK_CLIMBING):
        r = client.post("/api/v1/climbing/predict", json=payload)
    assert r.status_code == 200


def test_predict_with_all_optional_fields(client):
    payload = {**BASE, "dead_hang_seconds": 60, "max_pullups": 15}
    with patch("api.services.climbing_service.predict", return_value=MOCK_CLIMBING):
        r = client.post("/api/v1/climbing/predict", json=payload)
    assert r.status_code == 200


# ---------------------------------------------------------------------------
# Validation des entrées
# ---------------------------------------------------------------------------

def test_age_too_young(client):
    r = client.post("/api/v1/climbing/predict", json={**BASE, "age": 5})
    assert r.status_code == 422


def test_age_too_old(client):
    r = client.post("/api/v1/climbing/predict", json={**BASE, "age": 90})
    assert r.status_code == 422


def test_age_boundary_min(client):
    with patch("api.services.climbing_service.predict", return_value=MOCK_CLIMBING):
        r = client.post("/api/v1/climbing/predict", json={**BASE, "age": 10})
    assert r.status_code == 200


def test_height_too_short(client):
    r = client.post("/api/v1/climbing/predict", json={**BASE, "height_cm": 120.0})
    assert r.status_code == 422


def test_height_too_tall(client):
    r = client.post("/api/v1/climbing/predict", json={**BASE, "height_cm": 230.0})
    assert r.status_code == 422


def test_weight_too_light(client):
    r = client.post("/api/v1/climbing/predict", json={**BASE, "weight_kg": 35.0})
    assert r.status_code == 422


def test_weight_too_heavy(client):
    r = client.post("/api/v1/climbing/predict", json={**BASE, "weight_kg": 140.0})
    assert r.status_code == 422


def test_years_climbing_negative(client):
    r = client.post("/api/v1/climbing/predict", json={**BASE, "years_climbing": -1})
    assert r.status_code == 422


def test_years_climbing_too_many(client):
    r = client.post("/api/v1/climbing/predict", json={**BASE, "years_climbing": 60})
    assert r.status_code == 422


def test_dead_hang_too_long(client):
    r = client.post("/api/v1/climbing/predict", json={**BASE, "dead_hang_seconds": 400})
    assert r.status_code == 422


def test_invalid_gender(client):
    r = client.post("/api/v1/climbing/predict", json={**BASE, "gender": 5})
    assert r.status_code == 422
