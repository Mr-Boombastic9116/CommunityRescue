import os
import sys
from datetime import datetime, timedelta, timezone

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Add backend directory to sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from app.main import app
from app.database.session import SessionLocal
from app.models.food_batch import FoodBatch
from app.models.user import User
from app.utils.dates import IST, parse_iso_datetime, format_utc_iso, to_naive_utc

client = TestClient(app)

def run_tests():
    print("=" * 70)
    print("COMMUNITY FOOD RESCUE NETWORK - TIMEZONE & EXPIRY VALIDATION SUITE")
    print("=" * 70)

    # 1. Register or login a test donor
    donor_email = "test_donor_tz@example.com"
    donor_password = "Password123!"
    
    # Try logging in, if fails register
    login_res = client.post("/api/auth/login", json={"email": donor_email, "password": donor_password})
    if login_res.status_code == 200:
        token = login_res.json()["access_token"]
    else:
        reg_res = client.post("/api/auth/register", json={
            "name": "Timezone Test Donor",
            "email": donor_email,
            "password": donor_password,
            "role": "donor",
            "phone": "+91 9876543210",
            "address": "MG Road, Bengaluru, Karnataka",
        })
        assert reg_res.status_code in [200, 201], f"Registration failed: {reg_res.text}"
        token = reg_res.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    print("[+] Donor authenticated successfully.")

    # Base test date in IST (Tomorrow to ensure future expiry)
    tomorrow = datetime.now(IST).date() + timedelta(days=1)
    
    # -------------------------------------------------------------------------
    # TEST A: calculate-expiry endpoint formats approved_maximum_expiry with 'Z'
    # -------------------------------------------------------------------------
    print("\n--- TEST A: Calculate Expiry Endpoint Output ---")
    prep_ist_10am = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 10, 0, 0, tzinfo=IST)
    calc_res = client.post("/api/donations/calculate-expiry", json={
        "food_name": "Vegetable Biryani",
        "food_category": "Cooked Meals",
        "storage_condition": "ambient",
        "prepared_at": prep_ist_10am.isoformat(),
    }, headers=headers)
    assert calc_res.status_code == 200, f"Calculate expiry failed: {calc_res.text}"
    calc_data = calc_res.json()
    appr_max = calc_data["approved_maximum_expiry"]
    print(f"Input Prep (IST): {prep_ist_10am.isoformat()}")
    print(f"Max Holding Hours: {calc_data['max_holding_hours']}h")
    print(f"Approved Max Expiry: {appr_max}")
    assert appr_max.endswith("Z"), f"Expected approved_maximum_expiry to end with 'Z', got: {appr_max}"
    
    # In IST: 10:00 AM + 4 hours = 14:00 (2:00 PM) IST = 08:30 UTC
    parsed_appr = parse_iso_datetime(appr_max).astimezone(IST)
    print(f"Parsed in IST: {parsed_appr.strftime('%I:%M %p')}")
    assert parsed_appr.hour == 14 and parsed_appr.minute == 0, f"Expected 02:00 PM IST, got {parsed_appr}"
    print("[PASS] Test A: calculate-expiry returned valid UTC ISO ending in 'Z' (14:00 IST).")

    # -------------------------------------------------------------------------
    # 6 MANDATORY TEST CASES
    # -------------------------------------------------------------------------
    print("\n--- 6 MANDATORY TIMEZONE TEST CASES ---")

    # Case 1: 10:00 AM prep -> 11:00 AM exp: Valid (1 hour later)
    print("\n[Case 1] 10:00 AM IST prep -> 11:00 AM IST exp (Valid)")
    exp_ist_11am = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 11, 0, 0, tzinfo=IST)
    res_c1 = client.post("/api/donations", json={
        "food_name": "Case 1 Food",
        "food_category": "Cooked Meals",
        "quantity": 10,
        "unit": "servings",
        "storage_condition": "ambient",
        "prepared_at": prep_ist_10am.isoformat(),
        "expiry_time": exp_ist_11am.isoformat(),
        "pickup_address": "Test Address Case 1",
    }, headers=headers)
    assert res_c1.status_code == 201, f"Expected 201, got {res_c1.status_code}: {res_c1.text}"
    c1_batch = res_c1.json()
    assert c1_batch["prepared_at"].endswith("Z")
    assert c1_batch["expiry_time"].endswith("Z")
    print(f"Created batch {c1_batch['batch_id']}: Prep={c1_batch['prepared_at']}, Exp={c1_batch['expiry_time']}")
    print("[PASS] Case 1 Validated.")

    # Case 2: 10:00 AM prep -> 4:00 PM exp: Valid (6h hot holding)
    print("\n[Case 2] 10:00 AM IST prep -> 4:00 PM IST exp (Valid for hot holding 6h)")
    exp_ist_4pm = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 16, 0, 0, tzinfo=IST)
    res_c2 = client.post("/api/donations", json={
        "food_name": "Case 2 Food",
        "food_category": "Cooked Meals",
        "quantity": 15,
        "unit": "servings",
        "storage_condition": "hot_holding",
        "prepared_at": prep_ist_10am.isoformat(),
        "expiry_time": exp_ist_4pm.isoformat(),
        "pickup_address": "Test Address Case 2",
    }, headers=headers)
    assert res_c2.status_code == 201, f"Expected 201, got {res_c2.status_code}: {res_c2.text}"
    c2_batch = res_c2.json()
    assert c2_batch["prepared_at"].endswith("Z")
    assert c2_batch["expiry_time"].endswith("Z")
    print(f"Created batch {c2_batch['batch_id']}: Prep={c2_batch['prepared_at']}, Exp={c2_batch['expiry_time']}")
    print("[PASS] Case 2 Validated.")

    # Case 3: 10:00 AM prep -> 9:00 AM exp: Reject (1h earlier)
    print("\n[Case 3] 10:00 AM IST prep -> 9:00 AM IST exp (Reject: earlier)")
    exp_ist_9am = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 9, 0, 0, tzinfo=IST)
    res_c3 = client.post("/api/donations", json={
        "food_name": "Case 3 Food",
        "food_category": "Cooked Meals",
        "quantity": 5,
        "unit": "servings",
        "storage_condition": "ambient",
        "prepared_at": prep_ist_10am.isoformat(),
        "expiry_time": exp_ist_9am.isoformat(),
        "pickup_address": "Test Address Case 3",
    }, headers=headers)
    assert res_c3.status_code in [400, 422], f"Expected 400 or 422, got {res_c3.status_code}"
    assert "Expiry time must be strictly later than preparation time." in res_c3.text, f"Unexpected error detail: {res_c3.text}"
    print(f"Correctly rejected with response: {res_c3.status_code} - {res_c3.json()}")
    print("[PASS] Case 3 Validated.")

    # Case 4: 10:00 AM prep -> 10:00 AM exp: Reject (equal)
    print("\n[Case 4] 10:00 AM IST prep -> 10:00 AM IST exp (Reject: equal)")
    res_c4 = client.post("/api/donations", json={
        "food_name": "Case 4 Food",
        "food_category": "Cooked Meals",
        "quantity": 5,
        "unit": "servings",
        "storage_condition": "ambient",
        "prepared_at": prep_ist_10am.isoformat(),
        "expiry_time": prep_ist_10am.isoformat(),
        "pickup_address": "Test Address Case 4",
    }, headers=headers)
    assert res_c4.status_code in [400, 422], f"Expected 400 or 422, got {res_c4.status_code}"
    assert "Expiry time must be strictly later than preparation time." in res_c4.text, f"Unexpected error detail: {res_c4.text}"
    print(f"Correctly rejected with response: {res_c4.status_code} - {res_c4.json()}")
    print("[PASS] Case 4 Validated.")

    # Case 5: 10:00 AM prep -> 3:00 PM exp: Valid (5h later, within 6h hot holding)
    print("\n[Case 5] 10:00 AM IST prep -> 3:00 PM IST exp (Valid for hot holding 6h)")
    exp_ist_3pm = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 15, 0, 0, tzinfo=IST)
    res_c5 = client.post("/api/donations", json={
        "food_name": "Case 5 Food",
        "food_category": "Cooked Meals",
        "quantity": 20,
        "unit": "servings",
        "storage_condition": "hot_holding",
        "prepared_at": prep_ist_10am.isoformat(),
        "expiry_time": exp_ist_3pm.isoformat(),
        "pickup_address": "Test Address Case 5",
    }, headers=headers)
    assert res_c5.status_code == 201, f"Expected 201, got {res_c5.status_code}: {res_c5.text}"
    c5_batch = res_c5.json()
    assert c5_batch["prepared_at"].endswith("Z")
    assert c5_batch["expiry_time"].endswith("Z")
    print(f"Created batch {c5_batch['batch_id']}: Prep={c5_batch['prepared_at']}, Exp={c5_batch['expiry_time']}")
    print("[PASS] Case 5 Validated.")

    # Case 6: 11:30 PM prep -> 12:30 AM next day exp: Valid (rollover across midnight)
    print("\n[Case 6] 11:30 PM IST prep -> 12:30 AM next day IST exp (Valid midnight span)")
    prep_ist_1130pm = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 23, 30, 0, tzinfo=IST)
    day_after = tomorrow + timedelta(days=1)
    exp_ist_0030am = datetime(day_after.year, day_after.month, day_after.day, 0, 30, 0, tzinfo=IST)
    res_c6 = client.post("/api/donations", json={
        "food_name": "Case 6 Midnight Food",
        "food_category": "Cooked Meals",
        "quantity": 12,
        "unit": "servings",
        "storage_condition": "ambient",
        "prepared_at": prep_ist_1130pm.isoformat(),
        "expiry_time": exp_ist_0030am.isoformat(),
        "pickup_address": "Test Address Case 6",
    }, headers=headers)
    assert res_c6.status_code == 201, f"Expected 201, got {res_c6.status_code}: {res_c6.text}"
    c6_batch = res_c6.json()
    assert c6_batch["prepared_at"].endswith("Z")
    assert c6_batch["expiry_time"].endswith("Z")
    print(f"Created batch {c6_batch['batch_id']}: Prep={c6_batch['prepared_at']}, Exp={c6_batch['expiry_time']}")
    print("[PASS] Case 6 Validated.")

    # -------------------------------------------------------------------------
    # TEST B: Maximum Holding Duration Exceeded (Cooked Meals ambient > 4 hours)
    # -------------------------------------------------------------------------
    print("\n--- TEST B: Exceeding Maximum Holding Duration ---")
    exp_ist_6pm = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 18, 0, 0, tzinfo=IST)
    res_exceeded = client.post("/api/donations", json={
        "food_name": "Exceeded Duration Food",
        "food_category": "Cooked Meals",
        "quantity": 10,
        "unit": "servings",
        "storage_condition": "ambient",  # Max holding is 4.0 hours, 10 AM to 6 PM is 8 hours
        "prepared_at": prep_ist_10am.isoformat(),
        "expiry_time": exp_ist_6pm.isoformat(),
        "pickup_address": "Test Address Exceeded",
    }, headers=headers)
    assert res_exceeded.status_code == 400, f"Expected 400, got {res_exceeded.status_code}"
    print(f"Correctly rejected with 400: {res_exceeded.json()['detail']}")
    print("[PASS] Test B: Exceeded maximum holding duration rejected.")

    # -------------------------------------------------------------------------
    # TEST C: MariaDB Direct Inspection & Roundtrip Preservation
    # -------------------------------------------------------------------------
    print("\n--- TEST C: Database Storage and Local Time Roundtrip ---")
    db = SessionLocal()
    try:
        db_batch = db.query(FoodBatch).filter(FoodBatch.batch_id == c1_batch["batch_id"]).first()
        assert db_batch is not None
        print(f"Raw MariaDB stored prepared_at (naive UTC): {db_batch.prepared_at}")
        print(f"Raw MariaDB stored expiry_time (naive UTC): {db_batch.expiry_time}")
        
        # In UTC, 10:00 AM IST should be 04:30:00 UTC
        assert db_batch.prepared_at.hour == 4 and db_batch.prepared_at.minute == 30
        # In UTC, 11:00 AM IST should be 05:30:00 UTC
        assert db_batch.expiry_time.hour == 5 and db_batch.expiry_time.minute == 30
        
        # When read back through API:
        get_res = client.get(f"/api/donations/{c1_batch['batch_id']}", headers=headers)
        assert get_res.status_code == 200
        fetched = get_res.json()
        assert fetched["prepared_at"].endswith("Z")
        assert fetched["expiry_time"].endswith("Z")
        
        # Convert fetched to IST:
        fetched_prep_ist = parse_iso_datetime(fetched["prepared_at"]).astimezone(IST)
        fetched_exp_ist = parse_iso_datetime(fetched["expiry_time"]).astimezone(IST)
        
        print(f"Fetched Prep converted to IST: {fetched_prep_ist.strftime('%I:%M %p')}")
        print(f"Fetched Exp converted to IST: {fetched_exp_ist.strftime('%I:%M %p')}")
        
        assert fetched_prep_ist.hour == 10 and fetched_prep_ist.minute == 0
        assert fetched_exp_ist.hour == 11 and fetched_exp_ist.minute == 0
        print("[PASS] Test C: Stored UTC and returned IST match original inputs with 100% precision.")
    finally:
        db.close()

    print("\n" + "=" * 70)
    print("ALL TIMEZONE & EXPIRY VALIDATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()

