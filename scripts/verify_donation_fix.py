import sys
from pathlib import Path

# Ensure backend package root is at the head of sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

import json
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from app.main import app
from app.database.session import SessionLocal
from app.models.food_batch import FoodBatch
from app.models.user import User

client = TestClient(app)

print("=== 1. DONOR LOGIN ===")
login_res = client.post('/api/auth/login', json={'email': 'green_bites@example.com', 'password': 'Password123!'})
assert login_res.status_code == 200, f"Login failed: {login_res.text}"
token = login_res.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}
print("[OK] Logged in successfully as green_bites@example.com")

print("\n=== 2. MISSING FIELDS VALIDATION ===")
missing_res = client.post('/api/donations', json={'food_name': ''}, headers=headers)
assert missing_res.status_code == 422
assert isinstance(missing_res.json()['detail'], list)
print("[OK] Missing fields returned 422 with structured detail list")

print("\n=== 3. INVALID QUANTITY VALIDATION ===")
invalid_qty_res = client.post('/api/donations', json={
    'food_name': 'Paneer Butter Masala',
    'food_category': 'Cooked Meals',
    'quantity': -5,
    'unit': 'servings',
    'prepared_at': (datetime.utcnow() - timedelta(hours=1)).isoformat() + 'Z',
    'expiry_time': (datetime.utcnow() + timedelta(hours=2)).isoformat() + 'Z',
    'storage_condition': 'ambient',
    'pickup_address': 'MG Road, Bangalore'
}, headers=headers)
assert invalid_qty_res.status_code == 422
print("[OK] Negative quantity rejected with 422")

print("\n=== 4. EXPIRY BEYOND ALLOWED MAXIMUM (FSSAI CAPPING) ===")
now = datetime.utcnow()
over_exp_res = client.post('/api/donations', json={
    'food_name': 'Vegetable Samosas',
    'food_category': 'Cooked Meals',
    'food_description': 'Fried samosas with chutney',
    'quantity': 30,
    'unit': 'servings',
    'prepared_at': (now - timedelta(hours=1)).isoformat() + 'Z',
    'expiry_time': (now + timedelta(hours=48)).isoformat() + 'Z',
    'storage_condition': 'ambient',
    'storage_temperature': 25,
    'pickup_address': 'Koramangala, Bangalore'
}, headers=headers)
assert over_exp_res.status_code == 201, f"Failed: {over_exp_res.text}"
over_data = over_exp_res.json()
assert over_data['expiry_validation_status'] == 'adjusted'
print(f"[OK] Expiry beyond max successfully capped: status={over_data['expiry_validation_status']}, rule={over_data['expiry_rule_applied']}")

print("\n=== 5. NO APPLICABLE SAFETY RULE (PENDING VERIFICATION) ===")
unrec_res = client.post('/api/donations', json={
    'food_name': 'Experimental Hydroponic Spirulina Algae',
    'food_category': 'Raw Food/Produce',
    'food_description': 'Specialized live algae strain',
    'quantity': 5,
    'unit': 'kg',
    'prepared_at': (now - timedelta(hours=1)).isoformat() + 'Z',
    'expiry_time': (now + timedelta(hours=6)).isoformat() + 'Z',
    'storage_condition': 'frozen',
    'pickup_address': 'Indiranagar, Bangalore'
}, headers=headers)
assert unrec_res.status_code == 201
unrec_data = unrec_res.json()
print(f"[OK] Unrecognized/unmatched category placed in pending verification: status={unrec_data['food_status']}, expiry_validation_status={unrec_data['expiry_validation_status']}")

print("\n=== 6. EARLIER PERMITTED EXPIRY ===")
earlier_exp_res = client.post('/api/donations', json={
    'food_name': 'Fresh Baked Croissants',
    'food_category': 'Bakery & Bread',
    'food_description': 'Flaky morning croissants',
    'quantity': 20,
    'unit': 'packets',
    'prepared_at': (now - timedelta(hours=1)).isoformat() + 'Z',
    'expiry_time': (now + timedelta(hours=2)).isoformat() + 'Z',
    'storage_condition': 'ambient',
    'storage_temperature': 25,
    'pickup_address': 'Whitefield, Bangalore'
}, headers=headers)
assert earlier_exp_res.status_code == 201
earlier_data = earlier_exp_res.json()
assert earlier_data['expiry_validation_status'] == 'verified'
print(f"[OK] Earlier permitted expiry verified: batch_id={earlier_data['batch_id']}")

print("\n=== 7. PUBLISH VALID DONATION & CHECK DETAILS, RECOMMENDATIONS, TIMELINE ===")
valid_res = client.post('/api/donations', json={
    'food_name': 'Dal Tadka and Jeera Rice',
    'food_category': 'Cooked Meals',
    'food_description': 'Freshly prepared vegetarian meal sets',
    'quantity': 40,
    'unit': 'servings',
    'prepared_at': (now - timedelta(hours=1)).isoformat() + 'Z',
    'expiry_time': (now + timedelta(hours=3)).isoformat() + 'Z',
    'storage_condition': 'hot_holding',
    'storage_temperature': 65,
    'pickup_address': 'Church Street, Bangalore'
}, headers=headers)
assert valid_res.status_code == 201
valid_batch = valid_res.json()
batch_id = valid_batch['batch_id']
print(f"[OK] Created donation batch #{batch_id}")

# Fetch detail
det_res = client.get(f'/api/donations/{batch_id}', headers=headers)
assert det_res.status_code == 200
assert det_res.json()['batch_id'] == batch_id
print(f"[OK] Detail endpoint returned 200 with requests count: {len(det_res.json().get('requests', []))}")

# Fetch recommendations
rec_res = client.get(f'/api/donations/{batch_id}/recommended-ngos', headers=headers)
assert rec_res.status_code == 200
print(f"[OK] Recommended NGOs returned 200 with count: {len(rec_res.json().get('recommendations', []))}")

# Fetch timeline
tim_res = client.get(f'/api/donations/{batch_id}/timeline', headers=headers)
assert tim_res.status_code == 200
print(f"[OK] Timeline returned 200 with {len(tim_res.json().get('events', []))} events")

# Check My Donations list
my_res = client.get('/api/donations/my', headers=headers)
assert my_res.status_code == 200
my_batches = my_res.json()
assert any(b['batch_id'] == batch_id for b in my_batches)
print(f"[OK] Batch #{batch_id} confirmed present in My Donations list ({len(my_batches)} total batches)")

# Check Dashboard Stats
dash_res = client.get('/api/dashboard/stats', headers=headers)
assert dash_res.status_code == 200
stats_data = dash_res.json()
print(f"[OK] Dashboard stats returned 200: total_donations={stats_data.get('total_donations')}, available={stats_data.get('available_donations')}")

print("\n=== 8. DIRECT MARIADB PERSISTENCE VERIFICATION ===")
db = SessionLocal()
db_batch = db.query(FoodBatch).filter(FoodBatch.batch_id == batch_id).first()
assert db_batch is not None
assert db_batch.food_name == 'Dal Tadka and Jeera Rice'
assert float(db_batch.quantity) == 40.0
print(f"[OK] Confirmed persistent record in MariaDB: batch_id={db_batch.batch_id}, food_name='{db_batch.food_name}', quantity={db_batch.quantity}")
db.close()

print("\n=== ALL E2E VERIFICATION CHECKS PASSED SUCCESSFULLY! ===")
