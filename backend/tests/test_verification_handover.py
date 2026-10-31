import uuid
from datetime import datetime, timedelta
import pytest
from app.services.verification_service import VerificationService

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

def test_otp_hashing_and_generation():
    plain, hashed, qr = VerificationService.generate_otp()
    assert len(plain) == 6
    assert plain.isdigit()
    assert len(hashed) == 64  # SHA-256
    assert len(qr) > 20
    assert VerificationService.hash_code(plain) == hashed

def test_handover_verification_workflow(client):
    donor_tok = create_user(client, "donor", "Donor Hub")
    ngo_tok = create_user(client, "ngo", "Community NGO")
    vol_tok = create_user(client, "volunteer", "Courier Alex")
    other_vol_tok = create_user(client, "volunteer", "Other Courier")

    now = datetime.utcnow()

    # Create batch
    batch_res = client.post(
        "/api/donations",
        json={
            "food_name": "Vegetable Biryani",
            "food_category": "Cooked Meals",
            "quantity": 25.0,
            "unit": "servings",
            "prepared_at": (now - timedelta(hours=1)).isoformat(),
            "expiry_time": (now + timedelta(hours=2)).isoformat(),
            "pickup_address": "Hub Central",
        },
        headers={"Authorization": f"Bearer {donor_tok}"},
    )
    assert batch_res.status_code == 201
    batch_id = batch_res.json()["batch_id"]

    # NGO requests portion
    req_res = client.post(
        "/api/requests",
        json={"batch_id": batch_id, "requested_quantity": 20.0},
        headers={"Authorization": f"Bearer {ngo_tok}"},
    )
    assert req_res.status_code == 201
    request_id = req_res.json()["request_id"]

    # Courier Alex claims task
    claim_res = client.post(f"/api/volunteer/tasks/{request_id}/claim", headers={"Authorization": f"Bearer {vol_tok}"})
    assert claim_res.status_code == 200
    assert claim_res.json()["request_status"] == "assigned"

    # Courier is forbidden from inspecting handover code directly
    courier_inspect = client.get(f"/api/requests/{request_id}/handover-code", headers={"Authorization": f"Bearer {vol_tok}"})
    assert courier_inspect.status_code == 403

    # Donor obtains their Stage 1 Pickup code
    donor_code_res = client.get(f"/api/requests/{request_id}/handover-code", headers={"Authorization": f"Bearer {donor_tok}"})
    assert donor_code_res.status_code == 200
    pickup_code = donor_code_res.json()["handover_code"]
    assert pickup_code is not None

    # IDOR check: Other courier cannot verify Alex's task
    unauth_verify = client.post(
        f"/api/volunteer/tasks/{request_id}/verify-pickup",
        json={"code": pickup_code},
        headers={"Authorization": f"Bearer {other_vol_tok}"},
    )
    assert unauth_verify.status_code == 403

    # Invalid OTP attempt
    bad_attempt = client.post(
        f"/api/volunteer/tasks/{request_id}/verify-pickup",
        json={"code": "000000"},
        headers={"Authorization": f"Bearer {vol_tok}"},
    )
    assert bad_attempt.status_code == 400
    assert "Invalid pickup code" in bad_attempt.json()["detail"]

    # Valid OTP verification (Stage 1 -> collected)
    good_pickup = client.post(
        f"/api/volunteer/tasks/{request_id}/verify-pickup",
        json={"code": pickup_code, "notes": "Received biryani hot."},
        headers={"Authorization": f"Bearer {vol_tok}"},
    )
    assert good_pickup.status_code == 200
    assert good_pickup.json()["request_status"] == "collected"

    # Replay attack prevention: Same pickup code cannot be used again
    replay_attempt = client.post(
        f"/api/volunteer/tasks/{request_id}/verify-pickup",
        json={"code": pickup_code},
        headers={"Authorization": f"Bearer {vol_tok}"},
    )
    assert replay_attempt.status_code in [400, 403]

    # NGO obtains their Stage 2 Delivery code
    ngo_code_res = client.get(f"/api/requests/{request_id}/handover-code", headers={"Authorization": f"Bearer {ngo_tok}"})
    assert ngo_code_res.status_code == 200
    delivery_code = ngo_code_res.json()["handover_code"]
    assert delivery_code is not None

    # Valid Delivery OTP verification (Stage 2 -> delivered)
    good_delivery = client.post(
        f"/api/volunteer/tasks/{request_id}/verify-delivery",
        json={"code": delivery_code, "notes": "Delivered to shelter intake."},
        headers={"Authorization": f"Bearer {vol_tok}"},
    )
    assert good_delivery.status_code == 200
    assert good_delivery.json()["request_status"] == "delivered"

