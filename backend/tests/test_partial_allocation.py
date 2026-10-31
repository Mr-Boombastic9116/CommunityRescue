import pytest
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from fastapi.testclient import TestClient

def create_user(client, role, name):
    email = f"{role}_{uuid.uuid4().hex[:8]}@test.com"
    payload = {
        "name": name,
        "email": email,
        "password": "Password123!",
        "role": role,
        "phone": "+91 9123456789",
        "address": "Test Address",
        "organization_name": name,
    }
    res = client.post("/api/auth/register", json=payload)
    assert res.status_code == 201, res.text
    return res.json()["access_token"]

def test_partial_quantity_splitting(client):
    donor_tok = create_user(client, "donor", "Surplus Hotel")
    ngo1_tok = create_user(client, "ngo", "Shelter Alpha")
    ngo2_tok = create_user(client, "ngo", "Shelter Beta")
    ngo3_tok = create_user(client, "ngo", "Shelter Gamma")

    now = datetime.utcnow()

    # Step 1: Donor creates donation of 50 kg
    batch_res = client.post(
        "/api/donations",
        json={
            "food_name": "Nutritious Rice & Lentil Bowls",
            "food_category": "Cooked Meals",
            "quantity": 50.0,
            "unit": "kg",
            "prepared_at": (now - timedelta(hours=1)).isoformat(),
            "expiry_time": (now + timedelta(hours=3)).isoformat(),
            "pickup_address": "Hotel Kitchen Gate 2",
            "storage_condition": "ambient",
        },
        headers={"Authorization": f"Bearer {donor_tok}"},
    )
    assert batch_res.status_code == 201, batch_res.text
    batch_data = batch_res.json()
    batch_id = batch_data["batch_id"]
    assert batch_data["quantity"] == 50.0
    assert batch_data["food_status"] == "available"

    # Step 2: NGO 1 requests partial 20 kg
    req1_res = client.post(
        "/api/requests",
        json={
            "batch_id": batch_id,
            "requested_quantity": 20.0,
            "notes": "Shelter Alpha needs 20kg for lunch",
        },
        headers={"Authorization": f"Bearer {ngo1_tok}"},
    )
    assert req1_res.status_code == 201, req1_res.text
    req1_data = req1_res.json()
    assert req1_data["requested_quantity"] == 20.0
    assert req1_data["food_batch"]["food_status"] == "partially_reserved"
    assert req1_data["food_batch"]["remaining_quantity"] == 30.0

    # Step 3: NGO 2 requests remaining 30 kg
    req2_res = client.post(
        "/api/requests",
        json={
            "batch_id": batch_id,
            "requested_quantity": 30.0,
            "notes": "Shelter Beta needs 30kg",
        },
        headers={"Authorization": f"Bearer {ngo2_tok}"},
    )
    assert req2_res.status_code == 201, req2_res.text
    req2_data = req2_res.json()
    assert req2_data["requested_quantity"] == 30.0
    assert req2_data["food_batch"]["food_status"] == "reserved"
    assert req2_data["food_batch"]["remaining_quantity"] == 0.0

    # Step 4: NGO 3 tries to request 1 kg -> Should fail with 409 Conflict
    req3_res = client.post(
        "/api/requests",
        json={
            "batch_id": batch_id,
            "requested_quantity": 1.0,
        },
        headers={"Authorization": f"Bearer {ngo3_tok}"},
    )
    assert req3_res.status_code == 409
    assert "exceeds remaining available quantity" in req3_res.json()["detail"]

    # Step 5: NGO 1 cancels their 20 kg request -> Remaining should revert to 20 kg
    req1_id = req1_data["request_id"]
    cancel_res = client.post(
        f"/api/requests/{req1_id}/cancel",
        headers={"Authorization": f"Bearer {ngo1_tok}"},
    )
    assert cancel_res.status_code == 200, cancel_res.text

    # Verify batch is now partially_reserved with 20 kg available again
    get_batch = client.get(f"/api/donations/{batch_id}")
    assert get_batch.status_code == 200
    updated_batch = get_batch.json()
    assert updated_batch["food_status"] == "partially_reserved"
    assert updated_batch["remaining_quantity"] == 20.0
    assert updated_batch["allocated_quantity"] == 30.0
