import uuid
from datetime import datetime, timedelta

def get_donor_token(client):
    unique_email = f"donor_{uuid.uuid4().hex[:8]}@test.com"
    reg_payload = {
        "name": "Organic Mess",
        "email": unique_email,
        "password": "Password123!",
        "role": "donor",
        "phone": "+91 9999988888",
        "address": "College Hostel Campus",
    }
    res = client.post("/api/auth/register", json=reg_payload)
    return res.json()["access_token"]

def get_ngo_token(client):
    unique_email = f"ngo_{uuid.uuid4().hex[:8]}@test.com"
    reg_payload = {
        "name": "Help NGO",
        "email": unique_email,
        "password": "Password123!",
        "role": "ngo",
        "phone": "+91 8888877777",
        "address": "Community Center",
    }
    res = client.post("/api/auth/register", json=reg_payload)
    return res.json()["access_token"]

def test_create_and_manage_donation(client):
    donor_token = get_donor_token(client)
    now = datetime.utcnow()

    # Valid donation
    valid_payload = {
        "food_name": "Vegetable Pulao & Curry",
        "food_category": "Cooked Meals",
        "quantity": 50.0,
        "unit": "servings",
        "prepared_at": (now - timedelta(hours=1)).isoformat(),
        "expiry_time": (now + timedelta(hours=4)).isoformat(),
        "pickup_address": "Hostel Block B Gate",
    }

    res = client.post("/api/donations", json=valid_payload, headers={"Authorization": f"Bearer {donor_token}"})
    assert res.status_code == 201
    batch_data = res.json()
    batch_id = batch_data["batch_id"]
    assert batch_data["food_status"] == "available"
    assert batch_data["food_name"] == "Vegetable Pulao & Curry"

    # My donations endpoint
    res_my = client.get("/api/donations/my", headers={"Authorization": f"Bearer {donor_token}"})
    assert res_my.status_code == 200
    my_batches = res_my.json()
    assert any(b["batch_id"] == batch_id for b in my_batches)

    # Edit donation
    update_payload = {"quantity": 65.0}
    res_edit = client.put(f"/api/donations/{batch_id}", json=update_payload, headers={"Authorization": f"Bearer {donor_token}"})
    assert res_edit.status_code == 200
    assert res_edit.json()["quantity"] == 65.0

    # Authorization check: NGO cannot edit this donation
    ngo_token = get_ngo_token(client)
    res_unauth = client.put(f"/api/donations/{batch_id}", json={"quantity": 70.0}, headers={"Authorization": f"Bearer {ngo_token}"})
    assert res_unauth.status_code == 403

def test_donation_validation_errors(client):
    donor_token = get_donor_token(client)
    now = datetime.utcnow()

    # Error 1: Expiry before preparation time
    invalid_payload_1 = {
        "food_name": "Invalid Batch",
        "food_category": "Cooked Meals",
        "quantity": 20.0,
        "unit": "kg",
        "prepared_at": now.isoformat(),
        "expiry_time": (now - timedelta(hours=2)).isoformat(),
        "pickup_address": "Test Street",
    }
    res1 = client.post("/api/donations", json=invalid_payload_1, headers={"Authorization": f"Bearer {donor_token}"})
    assert res1.status_code in (400, 422)

    # Error 2: Negative quantity
    invalid_payload_2 = {
        "food_name": "Invalid Batch",
        "food_category": "Cooked Meals",
        "quantity": -5.0,
        "unit": "kg",
        "prepared_at": now.isoformat(),
        "expiry_time": (now + timedelta(hours=2)).isoformat(),
        "pickup_address": "Test Street",
    }
    res2 = client.post("/api/donations", json=invalid_payload_2, headers={"Authorization": f"Bearer {donor_token}"})
    assert res2.status_code == 422

