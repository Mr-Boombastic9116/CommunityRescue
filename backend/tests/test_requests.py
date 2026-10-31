import uuid
from datetime import datetime, timedelta

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
    return res.json()["access_token"]

def test_full_rescue_workflow(client):
    donor_tok = create_user(client, "donor", "Campus Dining")
    ngo_tok = create_user(client, "ngo", "City Food Shelter")
    vol_tok = create_user(client, "volunteer", "John Volunteer")

    now = datetime.utcnow()

    # 1. Donor creates donation
    batch_res = client.post(
        "/api/donations",
        json={
            "food_name": "Paneer Butter Masala & Roti",
            "food_category": "Cooked Meals",
            "quantity": 30.0,
            "unit": "servings",
            "storage_condition": "refrigerated",
            "prepared_at": (now - timedelta(hours=1)).isoformat(),
            "expiry_time": (now + timedelta(hours=6)).isoformat(),
            "pickup_address": "Dining Hall 2",
        },
        headers={"Authorization": f"Bearer {donor_tok}"},
    )
    assert batch_res.status_code == 201
    batch_id = batch_res.json()["batch_id"]

    # 2. NGO requests the donation
    req_res = client.post(
        "/api/requests",
        json={"batch_id": batch_id, "notes": "Urgent request for tonight"},
        headers={"Authorization": f"Bearer {ngo_tok}"},
    )
    assert req_res.status_code == 201
    request_id = req_res.json()["request_id"]
    assert req_res.json()["request_status"] == "requested"

    # 3. Volunteer views available tasks and claims it
    tasks_res = client.get("/api/volunteer/tasks/available", headers={"Authorization": f"Bearer {vol_tok}"})
    assert tasks_res.status_code == 200
    assert any(t["request_id"] == request_id for t in tasks_res.json())

    claim_res = client.post(f"/api/volunteer/tasks/{request_id}/claim", headers={"Authorization": f"Bearer {vol_tok}"})
    assert claim_res.status_code == 200
    assert claim_res.json()["request_status"] == "assigned"

    # 4. Donor retrieves secure pickup code, volunteer verifies and marks food as collected
    donor_code_res = client.get(f"/api/requests/{request_id}/handover-code", headers={"Authorization": f"Bearer {donor_tok}"})
    assert donor_code_res.status_code == 200
    pickup_code = donor_code_res.json()["handover_code"]
    assert pickup_code is not None and len(pickup_code) == 6

    col_res = client.post(
        f"/api/volunteer/tasks/{request_id}/verify-pickup",
        json={"code": pickup_code, "notes": "Food picked up in insulated containers."},
        headers={"Authorization": f"Bearer {vol_tok}"},
    )
    assert col_res.status_code == 200
    assert col_res.json()["request_status"] == "collected"

    # 5. NGO retrieves secure delivery code, volunteer verifies and marks delivery completed
    ngo_code_res = client.get(f"/api/requests/{request_id}/handover-code", headers={"Authorization": f"Bearer {ngo_tok}"})
    assert ngo_code_res.status_code == 200
    delivery_code = ngo_code_res.json()["handover_code"]
    assert delivery_code is not None and len(delivery_code) == 6

    deliv_res = client.post(
        f"/api/volunteer/tasks/{request_id}/verify-delivery",
        json={"code": delivery_code, "notes": "Delivered successfully to shelter incharge."},
        headers={"Authorization": f"Bearer {vol_tok}"},
    )
    assert deliv_res.status_code == 200
    assert deliv_res.json()["request_status"] == "delivered"

    # 6. Check delivery logs in request details
    detail_res = client.get(f"/api/requests/{request_id}", headers={"Authorization": f"Bearer {ngo_tok}"})
    assert detail_res.status_code == 200
    logs = detail_res.json()["delivery_logs"]
    actions = [l["action"] for l in logs]
    assert "FOOD_REQUESTED" in actions
    assert "PICKUP_ASSIGNED" in actions
    assert any("COLLECTED" in a.upper() for a in actions)
    assert any("COMPLETED" in a.upper() or "DELIVERED" in a.upper() for a in actions)

