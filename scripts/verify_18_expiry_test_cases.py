"""
Comprehensive Food Expiry Validation Test Script (18 Cases)
Validates the entire expiry workflow across frontend, backend, and MariaDB:
1. Valid food category and verified rule.
2. Preparation at 10:00 AM with a verified six-hour rule.
3. Expiry selected exactly at 4:00 PM (accepted).
4. Expiry selected before 4:00 PM (accepted).
5. Expiry selected after 4:00 PM (rejected HTTP 400).
6. Expiry earlier than preparation time (rejected HTTP 400).
7. Missing food category (rejected HTTP 422).
8. Missing storage condition (handled/validated).
9. No applicable verified safety rule (requires manual verification, pending_verification).
10. Changed preparation time (recalculates approved maximum).
11. Changed storage condition (recalculates holding duration).
12. Changed food category (recalculates holding duration).
13. Editing an existing donation (rejects if exceeding maximum or if expired).
14. Expired donation request attempt (rejected HTTP 400).
15. Volunteer assignment after expiry (rejected HTTP 400).
16. UTC/local timezone conversion (consistent naive UTC storage).
17. Manufacturer use-by date earlier than calculated maximum (caps approved maximum expiry).
18. Invalid or malformed datetime input (rejected HTTP 400/422).
"""

import os
import sys
import uuid
from datetime import datetime, timedelta

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Ensure backend root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_ROOT = os.path.join(PROJECT_ROOT, "backend")
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

from fastapi.testclient import TestClient
from app.main import app
from app.database.session import SessionLocal
from app.models.food_batch import FoodBatch
from app.models.pickup_request import PickupRequest
from app.models.user import User
from app.models.donor import Donor
from app.models.ngo import NGOPartner as NGO
from app.models.volunteer import Volunteer
from app.utils.dates import utc_now, to_naive_utc
from app.services.expiry_validation_service import ExpiryValidationService

client = TestClient(app)

def create_user_and_get_token(role: str, name: str) -> str:
    unique_email = f"{role}_{uuid.uuid4().hex[:8]}@test.com"
    payload = {
        "name": name,
        "email": unique_email,
        "password": "Password123!",
        "role": role,
        "phone": "+91 9876543210",
        "address": "123 Test Street",
    }
    if role == "ngo":
        payload["organization_name"] = f"{name} Org"
    res = client.post("/api/auth/register", json=payload)
    assert res.status_code == 201, f"Failed to register {role}: {res.text}"
    return res.json()["access_token"]

def run_18_test_cases():
    print("=" * 75)
    print("COMMUNITY FOOD RESCUE NETWORK - 18 FOOD EXPIRY VALIDATION TEST CASES")
    print("=" * 75)

    passed = 0
    failed = 0
    donor_tok = create_user_and_get_token("donor", "Chef Donor")
    ngo_tok = create_user_and_get_token("ngo", "Hope Shelter NGO")
    vol_tok = create_user_and_get_token("volunteer", "Express Courier")

    db = SessionLocal()

    # --- CASE 1: Valid food category and verified rule ---
    print("\n[Case 1] Valid food category and verified rule (Cooked Meals, Ambient)...")
    res1 = client.post("/api/donations/calculate-expiry", json={
        "food_name": "Vegetable Biryani",
        "food_category": "Cooked Meals",
        "storage_condition": "ambient",
        "prepared_at": "2026-10-31T10:00:00Z"
    })
    if res1.status_code == 200 and res1.json()["max_holding_hours"] == 4.0 and not res1.json()["requires_manual_verification"]:
        print("  ✓ PASS: Found 4.0h FSSAI holding rule for Cooked Meals (Ambient).")
        passed += 1
    else:
        print(f"  ✗ FAIL: {res1.status_code} - {res1.text}")
        failed += 1

    # --- CASE 2: Preparation at 10:00 AM with a verified 6-hour rule (Hot Holding) ---
    print("\n[Case 2] Preparation at 10:00 AM with a verified 6-hour rule (Cooked Meals, Hot Holding)...")
    prep_10am = "2026-10-31T10:00:00Z"
    res2 = client.post("/api/donations/calculate-expiry", json={
        "food_name": "Hot Stew & Rice",
        "food_category": "Cooked Meals",
        "storage_condition": "hot_holding",
        "prepared_at": prep_10am
    })
    data2 = res2.json()
    if res2.status_code == 200 and data2["max_holding_hours"] == 6.0 and "16:00:00" in data2["approved_maximum_expiry"]:
        print("  ✓ PASS: Correctly calculated 6.0h holding duration and 4:00 PM (16:00) latest permitted expiry.")
        passed += 1
    else:
        print(f"  ✗ FAIL: {res2.status_code} - {res2.text}")
        failed += 1

    # --- CASE 3: Expiry selected exactly at 4:00 PM (boundary case) ---
    print("\n[Case 3] Expiry selected exactly at 4:00 PM (boundary accepted)...")
    now = utc_now()
    # Let prep time be now - 2h, so max expiry is now + 4h (hot holding allows 6h from prep)
    prep_case3 = now - timedelta(hours=2)
    exp_case3 = prep_case3 + timedelta(hours=6) # Exactly max allowed
    res3 = client.post("/api/donations", json={
        "food_name": "Hot Khichdi",
        "food_category": "Cooked Meals",
        "quantity": 20.0,
        "unit": "servings",
        "prepared_at": prep_case3.isoformat(),
        "expiry_time": exp_case3.isoformat(),
        "storage_condition": "hot_holding",
        "pickup_address": "Main Kitchen Dock",
    }, headers={"Authorization": f"Bearer {donor_tok}"})
    if res3.status_code == 201 and res3.json()["food_status"] == "available":
        print(f"  ✓ PASS: Donation created successfully with boundary expiry ({res3.json()['batch_id']}).")
        passed += 1
    else:
        print(f"  ✗ FAIL: {res3.status_code} - {res3.text}")
        failed += 1

    # --- CASE 4: Expiry selected before 4:00 PM (earlier expiry allowed) ---
    print("\n[Case 4] Expiry selected before 4:00 PM (earlier expiry allowed)...")
    exp_case4 = prep_case3 + timedelta(hours=4) # 4 hours from prep, well within 6h max
    res4 = client.post("/api/donations", json={
        "food_name": "Hot Vegetable Dal",
        "food_category": "Cooked Meals",
        "quantity": 15.0,
        "unit": "servings",
        "prepared_at": prep_case3.isoformat(),
        "expiry_time": exp_case4.isoformat(),
        "storage_condition": "hot_holding",
        "pickup_address": "Main Kitchen Dock",
    }, headers={"Authorization": f"Bearer {donor_tok}"})
    if res4.status_code == 201 and res4.json()["food_status"] == "available":
        print(f"  ✓ PASS: Donation created with earlier expiry ({res4.json()['batch_id']}).")
        passed += 1
    else:
        print(f"  ✗ FAIL: {res4.status_code} - {res4.text}")
        failed += 1

    # --- CASE 5: Expiry selected after 4:00 PM (must reject with HTTP 400) ---
    print("\n[Case 5] Expiry selected after 4:00 PM (must reject with HTTP 400)...")
    exp_case5 = prep_case3 + timedelta(hours=6, minutes=30) # Exceeds 6h max by 30 mins
    res5 = client.post("/api/donations", json={
        "food_name": "Hot Dal Over-extended",
        "food_category": "Cooked Meals",
        "quantity": 10.0,
        "unit": "servings",
        "prepared_at": prep_case3.isoformat(),
        "expiry_time": exp_case5.isoformat(),
        "storage_condition": "hot_holding",
        "pickup_address": "Main Kitchen Dock",
    }, headers={"Authorization": f"Bearer {donor_tok}"})
    if res5.status_code == 400 and "exceeds the maximum permitted holding duration" in res5.json()["detail"]:
        print(f"  ✓ PASS: Correctly rejected with HTTP 400: '{res5.json()['detail']}'")
        passed += 1
    else:
        print(f"  ✗ FAIL: Expected 400, got {res5.status_code} - {res5.text}")
        failed += 1

    # --- CASE 6: Expiry earlier than preparation time (must reject with HTTP 400) ---
    print("\n[Case 6] Expiry earlier than preparation time (must reject with HTTP 400)...")
    res6 = client.post("/api/donations", json={
        "food_name": "Time Machine Food",
        "food_category": "Cooked Meals",
        "quantity": 10.0,
        "unit": "servings",
        "prepared_at": now.isoformat(),
        "expiry_time": (now - timedelta(hours=1)).isoformat(), # in past / before prep
        "storage_condition": "ambient",
        "pickup_address": "Mess",
    }, headers={"Authorization": f"Bearer {donor_tok}"})
    if res6.status_code in [400, 422]:
        print(f"  ✓ PASS: Correctly rejected impossible expiry before preparation time ({res6.status_code}).")
        passed += 1
    else:
        print(f"  ✗ FAIL: Expected 400/422, got {res6.status_code} - {res6.text}")
        failed += 1

    # --- CASE 7: Missing food category (validation error) ---
    print("\n[Case 7] Missing food category (must reject with HTTP 422)...")
    res7 = client.post("/api/donations", json={
        "food_name": "Mystery Dish",
        "quantity": 10.0,
        "unit": "servings",
        "prepared_at": (now - timedelta(hours=1)).isoformat(),
        "expiry_time": (now + timedelta(hours=2)).isoformat(),
        "storage_condition": "ambient",
        "pickup_address": "Mess",
    }, headers={"Authorization": f"Bearer {donor_tok}"})
    if res7.status_code == 422:
        print(f"  ✓ PASS: Correctly caught missing required field food_category (HTTP 422).")
        passed += 1
    else:
        print(f"  ✗ FAIL: Expected 422, got {res7.status_code}")
        failed += 1

    # --- CASE 8: Missing storage condition (defaults to ambient and applies ambient rule) ---
    print("\n[Case 8] Missing storage condition (handled/defaults properly)...")
    res8 = client.post("/api/donations", json={
        "food_name": "Default Storage Rice",
        "food_category": "Cooked Meals",
        "quantity": 10.0,
        "unit": "servings",
        "prepared_at": (now - timedelta(hours=1)).isoformat(),
        "expiry_time": (now + timedelta(hours=2)).isoformat(),
        "pickup_address": "Mess",
    }, headers={"Authorization": f"Bearer {donor_tok}"})
    if res8.status_code == 201 and res8.json()["storage_condition"] == "ambient":
        print(f"  ✓ PASS: Handled missing storage condition, defaulted to ambient safely.")
        passed += 1
    else:
        print(f"  ✗ FAIL: {res8.status_code} - {res8.text}")
        failed += 1

    # --- CASE 9: No applicable verified safety rule (sets manual verification / pending_verification) ---
    print("\n[Case 9] No applicable verified safety rule (requires manual verification)...")
    res9 = client.post("/api/donations", json={
        "food_name": "Extraterrestrial Fruit",
        "food_category": "Unknown Alien Category",
        "quantity": 5.0,
        "unit": "kg",
        "prepared_at": (now - timedelta(hours=1)).isoformat(),
        "expiry_time": (now + timedelta(hours=6)).isoformat(),
        "storage_condition": "subzero_nitrogen",
        "pickup_address": "Lab 4",
    }, headers={"Authorization": f"Bearer {donor_tok}"})
    if res9.status_code == 201:
        data9 = res9.json()
        if data9["food_status"] == "pending_verification" and data9["expiry_validation_status"] == "manual_verification_required":
            print(f"  ✓ PASS: Unverified category cleanly placed in pending_verification status.")
            passed += 1
        else:
            print(f"  ✗ FAIL: Status was {data9['food_status']}, validation {data9['expiry_validation_status']}")
            failed += 1
    else:
        print(f"  ✗ FAIL: {res9.status_code} - {res9.text}")
        failed += 1

    # --- CASE 10: Changed preparation time (recalculates approved maximum) ---
    print("\n[Case 10] Changed preparation time (dynamic recalculation)...")
    res10_t1 = client.post("/api/donations/calculate-expiry", json={
        "food_name": "Warm Pulao",
        "food_category": "Cooked Meals",
        "storage_condition": "hot_holding",
        "prepared_at": "2026-10-31T08:00:00Z"
    }).json()["approved_maximum_expiry"]
    res10_t2 = client.post("/api/donations/calculate-expiry", json={
        "food_name": "Warm Pulao",
        "food_category": "Cooked Meals",
        "storage_condition": "hot_holding",
        "prepared_at": "2026-10-31T11:00:00Z"
    }).json()["approved_maximum_expiry"]
    if "14:00:00" in res10_t1 and "17:00:00" in res10_t2:
        print(f"  ✓ PASS: Recalculated latest permitted expiry from 2:00 PM to 5:00 PM on prep time change.")
        passed += 1
    else:
        print(f"  ✗ FAIL: t1={res10_t1}, t2={res10_t2}")
        failed += 1

    # --- CASE 11: Changed storage condition (recalculates holding duration) ---
    print("\n[Case 11] Changed storage condition (ambient vs refrigerated)...")
    res11_amb = client.post("/api/donations/calculate-expiry", json={
        "food_name": "Cooked Stew",
        "food_category": "Cooked Meals",
        "storage_condition": "ambient",
        "prepared_at": prep_10am
    }).json()["max_holding_hours"]
    res11_ref = client.post("/api/donations/calculate-expiry", json={
        "food_name": "Cooked Stew",
        "food_category": "Cooked Meals",
        "storage_condition": "refrigerated",
        "prepared_at": prep_10am
    }).json()["max_holding_hours"]
    if res11_amb == 4.0 and res11_ref == 48.0:
        print(f"  ✓ PASS: Correctly recalculated max holding from 4.0h (ambient) to 48.0h (refrigerated).")
        passed += 1
    else:
        print(f"  ✗ FAIL: amb={res11_amb}, ref={res11_ref}")
        failed += 1

    # --- CASE 12: Changed food category (recalculates holding duration) ---
    print("\n[Case 12] Changed food category (Cooked Meals vs Dairy & Refrigerated vs Raw Food)...")
    res12_cooked = client.post("/api/donations/calculate-expiry", json={
        "food_name": "General Food",
        "food_category": "Cooked Meals",
        "storage_condition": "ambient",
        "prepared_at": prep_10am
    }).json()["max_holding_hours"]
    res12_dairy = client.post("/api/donations/calculate-expiry", json={
        "food_name": "Dairy Items",
        "food_category": "Dairy & Refrigerated",
        "storage_condition": "ambient",
        "prepared_at": prep_10am
    }).json()["max_holding_hours"]
    res12_raw = client.post("/api/donations/calculate-expiry", json={
        "food_name": "Produce Items",
        "food_category": "Raw Food/Produce",
        "storage_condition": "ambient",
        "prepared_at": prep_10am
    }).json()["max_holding_hours"]
    if res12_cooked == 4.0 and res12_dairy == 2.0 and res12_raw == 72.0:
        print(f"  ✓ PASS: Cooked Meals=4h, Dairy=2h, Raw Food/Produce=72h properly resolved from DB rules.")
        passed += 1
    else:
        print(f"  ✗ FAIL: cooked={res12_cooked}, dairy={res12_dairy}, raw={res12_raw}")
        failed += 1

    # --- CASE 13: Editing an existing donation (rejects if exceeding max expiry) ---
    print("\n[Case 13] Editing an existing donation (rejects if exceeding max expiry)...")
    # First create an available batch
    batch13 = client.post("/api/donations", json={
        "food_name": "Updatable Meal",
        "food_category": "Cooked Meals",
        "quantity": 10.0,
        "unit": "servings",
        "prepared_at": (now - timedelta(hours=1)).isoformat(),
        "expiry_time": (now + timedelta(hours=2)).isoformat(), # prep + 3h <= 4h max
        "storage_condition": "ambient",
        "pickup_address": "Door 1",
    }, headers={"Authorization": f"Bearer {donor_tok}"}).json()
    b_id = batch13["batch_id"]

    # Try to edit expiry to prep + 6h (exceeding 4h ambient max)
    res13_fail = client.put(f"/api/donations/{b_id}", json={
        "expiry_time": (now + timedelta(hours=5)).isoformat(), # prep + 6h
    }, headers={"Authorization": f"Bearer {donor_tok}"})
    if res13_fail.status_code == 400 and "exceeds the maximum permitted holding duration" in res13_fail.json()["detail"]:
        print(f"  ✓ PASS: Edit rejected with HTTP 400 when attempting to exceed max holding duration.")
        passed += 1
    else:
        print(f"  ✗ FAIL: {res13_fail.status_code} - {res13_fail.text}")
        failed += 1

    # --- CASE 14: Expired donation request attempt (rejected HTTP 400) ---
    print("\n[Case 14] Expired donation request attempt (rejected HTTP 400)...")
    # Manually create an expired batch in DB
    expired_batch = FoodBatch(
        donor_id=db.query(Donor).first().donor_id,
        food_name="Expired Bread",
        food_category="Bakery & Bread",
        quantity=10.0,
        unit="packets",
        prepared_at=now - timedelta(hours=50),
        expiry_time=now - timedelta(hours=2),
        effective_expiry_time=now - timedelta(hours=2),
        storage_condition="ambient",
        pickup_address="Old Pantry",
        food_status="expired",
    )
    db.add(expired_batch)
    db.commit()
    db.refresh(expired_batch)

    res14 = client.post("/api/requests", json={
        "batch_id": expired_batch.batch_id,
        "requested_quantity": 5.0,
        "unit": "packets"
    }, headers={"Authorization": f"Bearer {ngo_tok}"})
    if res14.status_code == 400 and "expired" in res14.json()["detail"]:
        print(f"  ✓ PASS: NGO request on expired donation rejected with HTTP 400: '{res14.json()['detail']}'")
        passed += 1
    else:
        print(f"  ✗ FAIL: {res14.status_code} - {res14.text}")
        failed += 1

    # --- CASE 15: Volunteer assignment after expiry (rejected HTTP 400) ---
    print("\n[Case 15] Volunteer assignment after expiry (rejected HTTP 400)...")
    # Create request on a batch that subsequently expired
    req_exp = PickupRequest(
        batch_id=expired_batch.batch_id,
        ngo_id=db.query(NGO).first().ngo_id,
        requested_quantity=2.0,
        unit="packets",
        request_status="requested",
        requested_at=now - timedelta(hours=1),
    )
    db.add(req_exp)
    db.commit()
    db.refresh(req_exp)

    res15 = client.post(f"/api/volunteer/tasks/{req_exp.request_id}/claim", headers={"Authorization": f"Bearer {vol_tok}"})
    if res15.status_code == 400 and "expired" in res15.json()["detail"]:
        print(f"  ✓ PASS: Courier task claim on expired food rejected with HTTP 400: '{res15.json()['detail']}'")
        passed += 1
    else:
        print(f"  ✗ FAIL: {res15.status_code} - {res15.text}")
        failed += 1

    # --- CASE 16: UTC/local timezone conversion (consistent naive UTC storage) ---
    print("\n[Case 16] UTC/local timezone conversion (naive UTC in MariaDB)...")
    # Query MariaDB record directly
    batch_db = db.query(FoodBatch).filter(FoodBatch.batch_id == res3.json()["batch_id"]).first()
    if batch_db and batch_db.prepared_at.tzinfo is None and batch_db.expiry_time.tzinfo is None:
        print(f"  ✓ PASS: Timestamps stored in MariaDB as consistent naive UTC datetimes without timezone drift.")
        passed += 1
    else:
        print(f"  ✗ FAIL: Timezone inconsistency in DB: {batch_db.prepared_at}")
        failed += 1

    # --- CASE 17: Manufacturer use-by date earlier than calculated maximum ---
    print("\n[Case 17] Manufacturer use-by date earlier than calculated maximum...")
    prep17 = now - timedelta(hours=1)
    # Packaged food ambient allows 720 hours (30 days)
    # But printed label is only 24 hours away
    pkg17 = prep17 + timedelta(hours=24)
    res17 = client.post("/api/donations/calculate-expiry", json={
        "food_name": "Sealed Canned Food Pack",
        "food_category": "Packaged & Canned",
        "storage_condition": "ambient",
        "prepared_at": prep17.isoformat(),
        "packaging_expiry": pkg17.isoformat()
    })
    data17 = res17.json()
    expected_iso = to_naive_utc(pkg17).isoformat()
    if data17["approved_maximum_expiry"] == expected_iso:
        print(f"  ✓ PASS: Approved maximum correctly capped to earlier manufacturer use-by date ({data17['approved_maximum_expiry']}).")
        passed += 1
    else:
        print(f"  ✗ FAIL: Expected {expected_iso}, got {data17['approved_maximum_expiry']}")
        failed += 1

    # --- CASE 18: Invalid or malformed datetime input (rejected HTTP 400/422) ---
    print("\n[Case 18] Invalid or malformed datetime input (rejected HTTP 400/422)...")
    res18 = client.post("/api/donations/calculate-expiry", json={
        "food_name": "Malformed Date Test",
        "food_category": "Cooked Meals",
        "storage_condition": "ambient",
        "prepared_at": "not-a-valid-timestamp"
    })
    if res18.status_code in [400, 422]:
        print(f"  ✓ PASS: Malformed ISO datetime input rejected cleanly with HTTP {res18.status_code}.")
        passed += 1
    else:
        print(f"  ✗ FAIL: Expected 400/422, got {res18.status_code}")
        failed += 1

    db.close()

    print("\n" + "=" * 75)
    print(f"ALL 18 TEST CASES SUMMARY: {passed} PASSED, {failed} FAILED (TOTAL 18)")
    print("=" * 75)
    return passed == 18

if __name__ == "__main__":
    success = run_18_test_cases()
    sys.exit(0 if success else 1)
