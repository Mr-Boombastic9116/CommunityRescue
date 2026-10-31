import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from app.main import app

def create_user(role, name):
    email = f"{role}_{uuid.uuid4().hex[:8]}@test.com"
    payload = {
        "name": name,
        "email": email,
        "password": "Password123!",
        "role": role,
        "phone": "+91 9123456789",
        "address": "Test Street",
    }
    with TestClient(app) as client:
        res = client.post("/api/auth/register", json=payload)
        return res.json()["access_token"]

def test_prevent_concurrent_claim():
    donor_tok = create_user("donor", "Concurrency Donor")
    ngo_tok = create_user("ngo", "Concurrency NGO")
    vol1_tok = create_user("volunteer", "Volunteer Alpha")
    vol2_tok = create_user("volunteer", "Volunteer Beta")

    now = datetime.utcnow()
    with TestClient(app) as client:
        batch_res = client.post(
            "/api/donations",
            json={
                "food_name": "Meals for Concurrency Test",
                "food_category": "Cooked Meals",
                "quantity": 25.0,
                "unit": "servings",
                "prepared_at": (now - timedelta(hours=1)).isoformat(),
                "expiry_time": (now + timedelta(hours=2)).isoformat(),
                "pickup_address": "Gate 1",
            },
            headers={"Authorization": f"Bearer {donor_tok}"},
        )
        batch_id = batch_res.json()["batch_id"]

        req_res = client.post(
            "/api/requests",
            json={"batch_id": batch_id},
            headers={"Authorization": f"Bearer {ngo_tok}"},
        )
        request_id = req_res.json()["request_id"]

    # Now simulate two simultaneous claim attempts using ThreadPoolExecutor
    def claim_attempt(token):
        with TestClient(app) as c:
            return c.post(
                f"/api/volunteer/tasks/{request_id}/claim",
                headers={"Authorization": f"Bearer {token}"},
            )

    with ThreadPoolExecutor(max_workers=2) as executor:
        f1 = executor.submit(claim_attempt, vol1_tok)
        f2 = executor.submit(claim_attempt, vol2_tok)
        r1 = f1.result()
        r2 = f2.result()

    statuses = [r1.status_code, r2.status_code]
    # Exactly one must succeed (200) and one must be rejected with 409 Conflict
    assert 200 in statuses, f"Expected a 200 success, got {statuses}"
    assert 409 in statuses, f"Expected a 409 Conflict, got {statuses}"

