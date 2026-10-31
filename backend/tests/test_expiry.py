import uuid
from datetime import datetime, timedelta
from app.models.food_batch import FoodBatch
from app.services.expiry_service import process_food_expiries

def test_expiry_processing(client, db_session):
    unique_email = f"donor_{uuid.uuid4().hex[:8]}@test.com"
    reg_payload = {
        "name": "Expiry Test Donor",
        "email": unique_email,
        "password": "Password123!",
        "role": "donor",
        "phone": "+91 9123456789",
        "address": "Campus Mess",
    }
    res = client.post("/api/auth/register", json=reg_payload)
    donor_tok = res.json()["access_token"]

    now = datetime.utcnow()
    # Create valid batch
    batch_res = client.post(
        "/api/donations",
        json={
            "food_name": "Soon Expiring Sandwiches",
            "food_category": "Bakery & Bread",
            "quantity": 15.0,
            "unit": "packets",
            "prepared_at": (now - timedelta(hours=2)).isoformat(),
            "expiry_time": (now + timedelta(hours=1)).isoformat(),
            "pickup_address": "Canteen Hall",
        },
        headers={"Authorization": f"Bearer {donor_tok}"},
    )
    batch_id = batch_res.json()["batch_id"]

    # Now manually simulate passage of time in database by updating expiry_time to past
    b = db_session.query(FoodBatch).filter(FoodBatch.batch_id == batch_id).first()
    assert b is not None, "FoodBatch should exist"
    b.expiry_time = now - timedelta(minutes=5)
    db_session.commit()

    # Run process_food_expiries
    expired_count = process_food_expiries(db_session)
    assert expired_count >= 1

    db_session.refresh(b)
    assert b.food_status == "expired"
