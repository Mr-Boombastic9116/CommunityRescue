import uuid
from datetime import datetime, timedelta
import pytest

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

def test_batch_and_request_timeline(client):
    donor_tok = create_user(client, "donor", "Timeline Donor")
    ngo_tok = create_user(client, "ngo", "Timeline NGO")

    now = datetime.utcnow()
    # Create batch
    b_res = client.post(
        "/api/donations",
        json={
            "food_name": "Vegetable Pulao",
            "food_category": "Cooked Meals",
            "quantity": 40.0,
            "unit": "servings",
            "prepared_at": (now - timedelta(hours=1)).isoformat(),
            "expiry_time": (now + timedelta(hours=2)).isoformat(),
            "pickup_address": "Koramangala 4th Block",
        },
        headers={"Authorization": f"Bearer {donor_tok}"},
    )
    assert b_res.status_code == 201
    batch_id = b_res.json()["batch_id"]

    # Request portion
    r_res = client.post(
        "/api/requests",
        json={"batch_id": batch_id, "requested_quantity": 25.0},
        headers={"Authorization": f"Bearer {ngo_tok}"},
    )
    assert r_res.status_code == 201
    req_id = r_res.json()["request_id"]

    # Batch timeline
    bt_res = client.get(f"/api/donations/{batch_id}/timeline", headers={"Authorization": f"Bearer {donor_tok}"})
    assert bt_res.status_code == 200
    events = bt_res.json()["events"]
    assert len(events) >= 2

    # Request 9-stage timeline
    rt_res = client.get(f"/api/requests/{req_id}/timeline", headers={"Authorization": f"Bearer {ngo_tok}"})
    assert rt_res.status_code == 200
    stages = rt_res.json()["stages"]
    assert len(stages) >= 5
    stage_keys = [s["key"] for s in stages]
    assert "created" in stage_keys
    assert "requested" in stage_keys
    assert "assigned" in stage_keys
    assert "collected" in stage_keys
    assert "delivered" in stage_keys

def test_in_app_notifications_flow(client):
    donor_tok = create_user(client, "donor", "Notif Donor")

    # Check notifications list
    n_res = client.get("/api/notifications", headers={"Authorization": f"Bearer {donor_tok}"})
    assert n_res.status_code == 200
    assert isinstance(n_res.json(), list)
