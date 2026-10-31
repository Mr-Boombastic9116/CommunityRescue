import uuid
from datetime import datetime, timedelta
import pytest
from app.services.matching_service import SmartMatchingService, haversine_distance_km

def create_user(client, role: str, name: str):
    email = f"{role}_{uuid.uuid4().hex[:8]}@example.com"
    payload = {
        "name": name,
        "email": email,
        "password": "Password123!",
        "role": role,
        "phone": "+91 9876543210",
        "address": f"Address for {name}",
    }
    res = client.post("/api/auth/register", json=payload)
    assert res.status_code == 201, res.text
    return res.json()["access_token"]

def test_haversine_distance():
    # Mumbai to Pune (~120 km)
    d = haversine_distance_km(19.0760, 72.8777, 18.5204, 73.8567)
    assert 110 < d < 135

    # Same location
    assert haversine_distance_km(12.9716, 77.5946, 12.9716, 77.5946) == 0.0

def test_matching_recommendations_endpoint(client):
    donor_tok = create_user(client, "donor", "Matching Test Donor")
    now = datetime.utcnow()
    # Create batch
    b_res = client.post(
        "/api/donations",
        json={
            "food_name": "Fresh Idli & Sambar",
            "food_category": "Cooked Meals",
            "quantity": 50.0,
            "unit": "servings",
            "prepared_at": (now - timedelta(hours=1)).isoformat(),
            "expiry_time": (now + timedelta(hours=2)).isoformat(),
            "pickup_address": "Indiranagar 100ft Rd",
            "latitude": 12.9783,
            "longitude": 77.6408,
        },
        headers={"Authorization": f"Bearer {donor_tok}"},
    )
    assert b_res.status_code == 201
    batch_id = b_res.json()["batch_id"]

    # Call recommended-ngos endpoint
    rec_res = client.get(f"/api/donations/{batch_id}/recommended-ngos", headers={"Authorization": f"Bearer {donor_tok}"})
    assert rec_res.status_code == 200
    data = rec_res.json()
    assert "recommendations" in data
    assert isinstance(data["recommendations"], list)
    if len(data["recommendations"]) > 0:
        first = data["recommendations"][0]
        assert "match_score" in first
        assert "score_breakdown" in first
        assert "distance" in first["score_breakdown"]
        assert "category_compatibility" in first["score_breakdown"]
        assert "quantity_suitability" in first["score_breakdown"]
        assert "expiry_urgency" in first["score_breakdown"]
        assert "availability" in first["score_breakdown"]
        assert "explanation" in first
