import uuid
from datetime import datetime, timedelta
import pytest

def get_donor_token(client):
    unique_email = f"donor_{uuid.uuid4().hex[:8]}@test.com"
    reg_payload = {
        "name": "Hostel Kitchen",
        "email": unique_email,
        "password": "Password123!",
        "role": "donor",
        "phone": "+91 9123456789",
        "address": "Campus Mess Hall",
    }
    res = client.post("/api/auth/register", json=reg_payload)
    return res.json()["access_token"]

def test_calculate_expiry_known_category(client):
    now = datetime.utcnow()
    payload = {
        "food_name": "Vegetable Pulao",
        "food_category": "Cooked Meals",
        "storage_condition": "ambient",
        "prepared_at": now.isoformat(),
    }
    res = client.post("/api/donations/calculate-expiry", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["max_holding_hours"] == 4.0
    assert data["requires_manual_verification"] is False
    assert data["approved_maximum_expiry"] is not None

def test_calculate_expiry_unknown_category_requires_verification(client):
    now = datetime.utcnow()
    payload = {
        "food_name": "Mysterious Special Concoction",
        "food_category": "Exotic Mystery Dish",
        "storage_condition": "unknown_condition",
        "prepared_at": now.isoformat(),
    }
    res = client.post("/api/donations/calculate-expiry", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["requires_manual_verification"] is True
    assert data["max_holding_hours"] is None

def test_create_donation_unverified_sets_pending_verification(client):
    token = get_donor_token(client)
    now = datetime.utcnow()
    payload = {
        "food_name": "Unverified Custom Dish",
        "food_category": "Exotic Mystery Dish",
        "quantity": 10.0,
        "unit": "kg",
        "prepared_at": (now - timedelta(hours=1)).isoformat(),
        "expiry_time": (now + timedelta(hours=12)).isoformat(),
        "storage_condition": "unknown_condition",
        "pickup_address": "Special Wing",
    }
    res = client.post("/api/donations", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 201
    batch = res.json()
    assert batch["food_status"] == "pending_verification"

def test_create_donation_caps_expiry_to_approved_max(client):
    token = get_donor_token(client)
    now = datetime.utcnow()
    prep_time = now - timedelta(hours=1)
    # Ambient cooked meal allows 4 hours max from prep time => max expiry is prep_time + 4h = now + 3h
    # Donor requests 10 hours => MUST be rejected with HTTP 400
    payload_exceeded = {
        "food_name": "Steamed Idli and Sambar",
        "food_category": "Cooked Meals",
        "storage_condition": "ambient",
        "quantity": 25.0,
        "unit": "servings",
        "prepared_at": prep_time.isoformat(),
        "expiry_time": (now + timedelta(hours=10)).isoformat(),
        "pickup_address": "Dining Hall Gate",
    }
    res_exceeded = client.post("/api/donations", json=payload_exceeded, headers={"Authorization": f"Bearer {token}"})
    assert res_exceeded.status_code == 400
    assert "exceeds the maximum permitted holding duration" in res_exceeded.json()["detail"]

    # When donor selects within permitted maximum (prep_time + 3h <= prep_time + 4h) => accepted with 201
    payload_valid = {
        "food_name": "Steamed Idli and Sambar",
        "food_category": "Cooked Meals",
        "storage_condition": "ambient",
        "quantity": 25.0,
        "unit": "servings",
        "prepared_at": prep_time.isoformat(),
        "expiry_time": (prep_time + timedelta(hours=3)).isoformat(),
        "pickup_address": "Dining Hall Gate",
    }
    res_valid = client.post("/api/donations", json=payload_valid, headers={"Authorization": f"Bearer {token}"})
    assert res_valid.status_code == 201
    batch = res_valid.json()
    assert batch["food_status"] == "available"
    assert batch["expiry_validation_status"] == "verified"
