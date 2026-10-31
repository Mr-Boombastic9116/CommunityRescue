import uuid
import pytest

def register_user(client, role):
    unique_email = f"{role}_{uuid.uuid4().hex[:8]}@test.com"
    payload = {
        "name": f"Perm Test {role.capitalize()}",
        "email": unique_email,
        "password": "Password123!",
        "role": role,
        "phone": "+91 9123456789",
        "address": "Test Avenue",
    }
    res = client.post("/api/auth/register", json=payload)
    assert res.status_code == 201
    return res.json()["access_token"]

def test_donor_cannot_create_ngo_request(client):
    donor_token = register_user(client, "donor")
    payload = {
        "batch_id": 1,
        "requested_quantity": 10.0,
    }
    res = client.post("/api/requests", json=payload, headers={"Authorization": f"Bearer {donor_token}"})
    assert res.status_code == 403
    assert "Access denied" in res.json()["detail"] or "not authorized" in res.json()["detail"]

def test_ngo_cannot_create_food_donation(client):
    ngo_token = register_user(client, "ngo")
    payload = {
        "food_name": "Unauthorized NGO Food",
        "food_category": "Cooked Meals",
        "quantity": 10.0,
        "unit": "kg",
        "pickup_address": "NGO Shelter",
    }
    res = client.post("/api/donations", json=payload, headers={"Authorization": f"Bearer {ngo_token}"})
    assert res.status_code == 403
    assert "Access denied" in res.json()["detail"] or "not authorized" in res.json()["detail"]

def test_volunteer_cannot_create_food_donation(client):
    vol_token = register_user(client, "volunteer")
    payload = {
        "food_name": "Unauthorized Volunteer Food",
        "food_category": "Cooked Meals",
        "quantity": 5.0,
        "unit": "kg",
        "pickup_address": "Street Corner",
    }
    res = client.post("/api/donations", json=payload, headers={"Authorization": f"Bearer {vol_token}"})
    assert res.status_code == 403

def test_unauthenticated_request_rejected(client):
    res = client.post("/api/donations", json={"food_name": "No Auth"})
    assert res.status_code in [401, 403]
