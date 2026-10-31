"""
Community Food Rescue Network - Synthetic Data Seeder
Populates MySQL database with realistic synthetic data for development, testing, and college demonstrations.
Location: Goa, India
Idempotent: Safe to run multiple times without duplicating records.
"""

import os
import sys
import argparse
from datetime import datetime, timedelta

# Ensure backend directory is in python search path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.database.session import SessionLocal, engine
from app.core.security import hash_password
from app.models.user import User
from app.models.donor import Donor
from app.models.ngo import NGOPartner
from app.models.volunteer import Volunteer
from app.models.food_batch import FoodBatch
from app.models.pickup_request import PickupRequest
from app.models.delivery_log import DeliveryLog
from app.models.notification import Notification

DEFAULT_PASSWORD = "Password123!"

# -----------------------------------------------------------------------------
# 1. SYNTHETIC USERS & PROFILES CONFIGURATION (Goa, India)
# -----------------------------------------------------------------------------

SYNTHETIC_DONORS = [
    {
        "email": "green_bites@example.com",
        "name": "Green Bites Organic Cafe",
        "donor_name": "Green Bites Organic Cafe",
        "phone": "+91 98221 12345",
        "address": "142 Dayanand Bandodkar Marg, Miramar, Panaji, Goa 403001",
        "latitude": 15.48600000,
        "longitude": 73.80800000,
    },
    {
        "email": "campus_mess@example.com",
        "name": "Goa University Dining Hall",
        "donor_name": "Goa University Dining Hall",
        "phone": "+91 98222 23456",
        "address": "Central Mess Block, Goa University Campus, Taleigao Plateau, Goa 403206",
        "latitude": 15.45780000,
        "longitude": 73.83350000,
    },
    {
        "email": "ritz_classic@example.com",
        "name": "Ritz Classic Seafood Restaurant",
        "donor_name": "Ritz Classic Seafood Restaurant",
        "phone": "+91 98223 34567",
        "address": "18th June Road, Opposite Municipal Market, Panaji, Goa 403001",
        "latitude": 15.49750000,
        "longitude": 73.82600000,
    },
    {
        "email": "bakers_street@example.com",
        "name": "Bakers Street Patisserie",
        "donor_name": "Bakers Street Patisserie",
        "phone": "+91 98224 45678",
        "address": "Chogm Road, Alto-Porvorim, Goa 403521",
        "latitude": 15.53200000,
        "longitude": 73.83100000,
    },
    {
        "email": "grand_hyatt_kitchen@example.com",
        "name": "Grand Hyatt Banquet Kitchen",
        "donor_name": "Grand Hyatt Banquet Kitchen",
        "phone": "+91 98225 56789",
        "address": "P.O. Goa University, Bambolim Bay, Goa 403206",
        "latitude": 15.44900000,
        "longitude": 73.85400000,
    },
    {
        "email": "spice_goa@example.com",
        "name": "Spice Goa Caterers & Kitchen",
        "donor_name": "Spice Goa Caterers & Kitchen",
        "phone": "+91 98226 67890",
        "address": "NH 66 Bypass, Karaswada, Mapusa, Goa 403507",
        "latitude": 15.60200000,
        "longitude": 73.81800000,
    },
]

SYNTHETIC_NGOS = [
    {
        "email": "care_foundation@example.com",
        "name": "Care & Hope Shelter",
        "ngo_name": "Care & Hope Shelter Home",
        "phone": "+91 83222 11001",
        "address": "Altinho Hill Road, Near Bishop's Palace, Panaji, Goa 403001",
        "latitude": 15.49500000,
        "longitude": 73.82900000,
    },
    {
        "email": "feed_all@example.com",
        "name": "Feed The Hungry Mission Goa",
        "ngo_name": "Feed The Hungry Mission Goa",
        "phone": "+91 83222 22002",
        "address": "Station Road, Near Railway Junction, Margao, Goa 403601",
        "latitude": 15.27500000,
        "longitude": 73.96200000,
    },
    {
        "email": "st_anthony_home@example.com",
        "name": "St. Anthony Children's Home",
        "ngo_name": "St. Anthony's Children's Home & Care",
        "phone": "+91 83222 33003",
        "address": "Duler Grounds, Mapusa, Goa 403507",
        "latitude": 15.59800000,
        "longitude": 73.81600000,
    },
    {
        "email": "pragati_trust@example.com",
        "name": "Pragati Community Kitchen",
        "ngo_name": "Pragati Community Welfare Center",
        "phone": "+91 83222 44004",
        "address": "Swatantra Path, Port Area, Vasco da Gama, Goa 403802",
        "latitude": 15.39800000,
        "longitude": 73.81400000,
    },
    {
        "email": "sneha_mandir@example.com",
        "name": "Sneha Mandir Welfare Foundation",
        "ngo_name": "Sneha Mandir Elderly Care & Food Center",
        "phone": "+91 83222 55005",
        "address": "Bandora, Near Ramnathi Temple Road, Ponda, Goa 403401",
        "latitude": 15.40100000,
        "longitude": 74.01300000,
    },
]

SYNTHETIC_VOLUNTEERS = [
    {
        "email": "alex_volunteer@example.com",
        "name": "Alex Rivera",
        "volunteer_name": "Alex Rivera",
        "phone": "+91 97654 32101",
        "availability_status": "available",
    },
    {
        "email": "priya_volunteer@example.com",
        "name": "Priya Sharma",
        "volunteer_name": "Priya Sharma",
        "phone": "+91 97654 32102",
        "availability_status": "available",
    },
    {
        "email": "rohan_volunteer@example.com",
        "name": "Rohan Fernandes",
        "volunteer_name": "Rohan Fernandes",
        "phone": "+91 97654 32103",
        "availability_status": "available",
    },
    {
        "email": "ananya_volunteer@example.com",
        "name": "Ananya Deshmukh",
        "volunteer_name": "Ananya Deshmukh",
        "phone": "+91 97654 32104",
        "availability_status": "available",
    },
    {
        "email": "vikram_volunteer@example.com",
        "name": "Vikram Naik",
        "volunteer_name": "Vikram Naik",
        "phone": "+91 97654 32105",
        "availability_status": "available",
    },
    {
        "email": "neha_volunteer@example.com",
        "name": "Neha Kamat",
        "volunteer_name": "Neha Kamat",
        "phone": "+91 97654 32106",
        "availability_status": "busy",
    },
    {
        "email": "samuel_volunteer@example.com",
        "name": "Samuel D'Souza",
        "volunteer_name": "Samuel D'Souza",
        "phone": "+91 97654 32107",
        "availability_status": "busy",
    },
    {
        "email": "fatima_volunteer@example.com",
        "name": "Fatima Bi Sheikh",
        "volunteer_name": "Fatima Bi Sheikh",
        "phone": "+91 97654 32108",
        "availability_status": "offline",
    },
    {
        "email": "rahul_volunteer@example.com",
        "name": "Rahul Vernekar",
        "volunteer_name": "Rahul Vernekar",
        "phone": "+91 97654 32109",
        "availability_status": "offline",
    },
]

# All synthetic emails for scoped cleanup and identification
ALL_SYNTHETIC_EMAILS = (
    [d["email"] for d in SYNTHETIC_DONORS] +
    [n["email"] for n in SYNTHETIC_NGOS] +
    [v["email"] for v in SYNTHETIC_VOLUNTEERS]
)

# -----------------------------------------------------------------------------
# 2. FOOD BATCHES DEFINITIONS (20 Total)
# Relative offsets from current UTC time for dynamic, repeatable demonstration
# -----------------------------------------------------------------------------

def get_synthetic_food_batches(now: datetime, donors_map: dict):
    return [
        # --- AVAILABLE BATCHES (6) ---
        # 1. Urgent expiry (<2h)
        {
            "code": "FB-01",
            "donor_email": "green_bites@example.com",
            "food_name": "Vegetable Pulao & Cucumber Raita",
            "food_category": "Cooked Meals",
            "quantity": 40.0,
            "unit": "servings",
            "prepared_at": now - timedelta(hours=2),
            "expiry_time": now + timedelta(hours=1, minutes=30),  # 1.5h left (URGENT)
            "food_status": "available",
        },
        # 2. Urgent expiry (<2h)
        {
            "code": "FB-02",
            "donor_email": "ritz_classic@example.com",
            "food_name": "Goan Fish Curry & Steamed Rice",
            "food_category": "Cooked Meals",
            "quantity": 35.0,
            "unit": "servings",
            "prepared_at": now - timedelta(hours=1, minutes=45),
            "expiry_time": now + timedelta(hours=1, minutes=45),  # 1.75h left (URGENT)
            "food_status": "available",
        },
        # 3. Later today (<5h)
        {
            "code": "FB-03",
            "donor_email": "bakers_street@example.com",
            "food_name": "Fresh Goan Poee & Mixed Vegetable Xacuti",
            "food_category": "Cooked Meals",
            "quantity": 50.0,
            "unit": "servings",
            "prepared_at": now - timedelta(hours=2),
            "expiry_time": now + timedelta(hours=4),  # 4h left
            "food_status": "available",
        },
        # 4. Later today (<6h)
        {
            "code": "FB-04",
            "donor_email": "campus_mess@example.com",
            "food_name": "Steamed Basmati Rice & Dal Tadka",
            "food_category": "Cooked Meals",
            "quantity": 60.0,
            "unit": "servings",
            "prepared_at": now - timedelta(hours=3),
            "expiry_time": now + timedelta(hours=5),  # 5h left
            "food_status": "available",
        },
        # 5. Fresh / Tomorrow (18h)
        {
            "code": "FB-05",
            "donor_email": "bakers_street@example.com",
            "food_name": "Assorted Artisan Bread & Baguettes",
            "food_category": "Bakery & Bread",
            "quantity": 25.0,
            "unit": "kg",
            "prepared_at": now - timedelta(hours=4),
            "expiry_time": now + timedelta(hours=18),  # 18h left
            "food_status": "available",
        },
        # 6. Fresh produce / Tomorrow (12h)
        {
            "code": "FB-06",
            "donor_email": "grand_hyatt_kitchen@example.com",
            "food_name": "Fresh Cut Seasonal Tropical Fruits",
            "food_category": "Fresh Produce",
            "quantity": 20.0,
            "unit": "kg",
            "prepared_at": now - timedelta(hours=2),
            "expiry_time": now + timedelta(hours=12),  # 12h left
            "food_status": "available",
        },

        # --- REQUESTED BATCHES (3) ---
        # 7.
        {
            "code": "FB-07",
            "donor_email": "green_bites@example.com",
            "food_name": "Fresh Vegetable Club Sandwiches",
            "food_category": "Bakery & Bread",
            "quantity": 45.0,
            "unit": "packs",
            "prepared_at": now - timedelta(hours=2),
            "expiry_time": now + timedelta(hours=3),
            "food_status": "requested",
        },
        # 8.
        {
            "code": "FB-08",
            "donor_email": "spice_goa@example.com",
            "food_name": "Paneer Butter Masala & Phulkas",
            "food_category": "Cooked Meals",
            "quantity": 30.0,
            "unit": "servings",
            "prepared_at": now - timedelta(hours=1, minutes=30),
            "expiry_time": now + timedelta(hours=4),
            "food_status": "requested",
        },
        # 9.
        {
            "code": "FB-09",
            "donor_email": "campus_mess@example.com",
            "food_name": "South Indian Tiffin: Idli, Vada & Sambar",
            "food_category": "Cooked Meals",
            "quantity": 50.0,
            "unit": "servings",
            "prepared_at": now - timedelta(hours=2),
            "expiry_time": now + timedelta(hours=3, minutes=30),
            "food_status": "requested",
        },

        # --- ASSIGNED BATCHES (3) ---
        # 10.
        {
            "code": "FB-10",
            "donor_email": "ritz_classic@example.com",
            "food_name": "Cooked Chicken Cafreal & Butter Pav",
            "food_category": "Cooked Meals",
            "quantity": 35.0,
            "unit": "servings",
            "prepared_at": now - timedelta(hours=3),
            "expiry_time": now + timedelta(hours=3),
            "food_status": "assigned",
        },
        # 11.
        {
            "code": "FB-11",
            "donor_email": "spice_goa@example.com",
            "food_name": "Vegetable Dum Biryani & Mirchi Salan",
            "food_category": "Cooked Meals",
            "quantity": 45.0,
            "unit": "servings",
            "prepared_at": now - timedelta(hours=2, minutes=30),
            "expiry_time": now + timedelta(hours=3, minutes=30),
            "food_status": "assigned",
        },
        # 12.
        {
            "code": "FB-12",
            "donor_email": "bakers_street@example.com",
            "food_name": "Banana Walnut Bread & Tea Cakes",
            "food_category": "Bakery & Bread",
            "quantity": 18.0,
            "unit": "kg",
            "prepared_at": now - timedelta(hours=4),
            "expiry_time": now + timedelta(hours=14),
            "food_status": "assigned",
        },

        # --- COLLECTED BATCHES (3) ---
        # 13.
        {
            "code": "FB-13",
            "donor_email": "campus_mess@example.com",
            "food_name": "Whole Wheat Chapatis & Aloo Gobi Dry",
            "food_category": "Cooked Meals",
            "quantity": 50.0,
            "unit": "servings",
            "prepared_at": now - timedelta(hours=3),
            "expiry_time": now + timedelta(hours=3),
            "food_status": "collected",
        },
        # 14.
        {
            "code": "FB-14",
            "donor_email": "grand_hyatt_kitchen@example.com",
            "food_name": "Continental Banquet Buffet Trays",
            "food_category": "Cooked Meals",
            "quantity": 40.0,
            "unit": "servings",
            "prepared_at": now - timedelta(hours=3, minutes=30),
            "expiry_time": now + timedelta(hours=2, minutes=30),
            "food_status": "collected",
        },
        # 15.
        {
            "code": "FB-15",
            "donor_email": "green_bites@example.com",
            "food_name": "Farm Fresh Spinach & Green Vegetables",
            "food_category": "Fresh Produce",
            "quantity": 15.0,
            "unit": "kg",
            "prepared_at": now - timedelta(hours=5),
            "expiry_time": now + timedelta(hours=20),
            "food_status": "collected",
        },

        # --- DELIVERED BATCHES (3) ---
        # 16.
        {
            "code": "FB-16",
            "donor_email": "ritz_classic@example.com",
            "food_name": "Goan Fish Thali Box Meals",
            "food_category": "Cooked Meals",
            "quantity": 30.0,
            "unit": "servings",
            "prepared_at": now - timedelta(hours=24),
            "expiry_time": now - timedelta(hours=14),
            "food_status": "delivered",
        },
        # 17.
        {
            "code": "FB-17",
            "donor_email": "bakers_street@example.com",
            "food_name": "Assorted Croissants & Sweet Buns",
            "food_category": "Bakery & Bread",
            "quantity": 16.0,
            "unit": "kg",
            "prepared_at": now - timedelta(hours=26),
            "expiry_time": now - timedelta(hours=10),
            "food_status": "delivered",
        },
        # 18.
        {
            "code": "FB-18",
            "donor_email": "spice_goa@example.com",
            "food_name": "Comfort Moong Dal Khichdi & Pickle",
            "food_category": "Cooked Meals",
            "quantity": 55.0,
            "unit": "servings",
            "prepared_at": now - timedelta(hours=30),
            "expiry_time": now - timedelta(hours=18),
            "food_status": "delivered",
        },

        # --- EXPIRED BATCHES (2) ---
        # 19.
        {
            "code": "FB-19",
            "donor_email": "campus_mess@example.com",
            "food_name": "Cooked Rajma Masala & Jeera Rice",
            "food_category": "Cooked Meals",
            "quantity": 40.0,
            "unit": "servings",
            "prepared_at": now - timedelta(hours=28),
            "expiry_time": now - timedelta(hours=6),  # Expired 6h ago
            "food_status": "expired",
        },
        # 20.
        {
            "code": "FB-20",
            "donor_email": "green_bites@example.com",
            "food_name": "Vegetable Samosas & Mint Chutney",
            "food_category": "Cooked Meals",
            "quantity": 60.0,
            "unit": "pieces",
            "prepared_at": now - timedelta(hours=20),
            "expiry_time": now - timedelta(hours=4),  # Expired 4h ago
            "food_status": "expired",
        },
    ]

# -----------------------------------------------------------------------------
# 3. PICKUP REQUESTS DEFINITIONS (15 Total)
# -----------------------------------------------------------------------------

def get_synthetic_pickup_requests(now: datetime):
    return [
        # --- REQUESTED (3) ---
        {
            "code": "PR-01",
            "batch_code": "FB-07",
            "ngo_email": "care_foundation@example.com",
            "volunteer_email": None,
            "request_status": "requested",
            "requested_at": now - timedelta(minutes=45),
            "assigned_at": None,
            "collected_at": None,
            "completed_at": None,
        },
        {
            "code": "PR-02",
            "batch_code": "FB-08",
            "ngo_email": "feed_all@example.com",
            "volunteer_email": None,
            "request_status": "requested",
            "requested_at": now - timedelta(minutes=30),
            "assigned_at": None,
            "collected_at": None,
            "completed_at": None,
        },
        {
            "code": "PR-03",
            "batch_code": "FB-09",
            "ngo_email": "st_anthony_home@example.com",
            "volunteer_email": None,
            "request_status": "requested",
            "requested_at": now - timedelta(minutes=20),
            "assigned_at": None,
            "collected_at": None,
            "completed_at": None,
        },

        # --- ASSIGNED (3) ---
        {
            "code": "PR-04",
            "batch_code": "FB-10",
            "ngo_email": "care_foundation@example.com",
            "volunteer_email": "alex_volunteer@example.com",
            "request_status": "assigned",
            "requested_at": now - timedelta(hours=2),
            "assigned_at": now - timedelta(hours=1, minutes=30),
            "collected_at": None,
            "completed_at": None,
        },
        {
            "code": "PR-05",
            "batch_code": "FB-11",
            "ngo_email": "st_anthony_home@example.com",
            "volunteer_email": "priya_volunteer@example.com",
            "request_status": "assigned",
            "requested_at": now - timedelta(hours=1, minutes=45),
            "assigned_at": now - timedelta(hours=1, minutes=15),
            "collected_at": None,
            "completed_at": None,
        },
        {
            "code": "PR-06",
            "batch_code": "FB-12",
            "ngo_email": "sneha_mandir@example.com",
            "volunteer_email": "rohan_volunteer@example.com",
            "request_status": "assigned",
            "requested_at": now - timedelta(hours=2, minutes=15),
            "assigned_at": now - timedelta(hours=1, minutes=40),
            "collected_at": None,
            "completed_at": None,
        },

        # --- COLLECTED (3) ---
        {
            "code": "PR-07",
            "batch_code": "FB-13",
            "ngo_email": "feed_all@example.com",
            "volunteer_email": "alex_volunteer@example.com",
            "request_status": "collected",
            "requested_at": now - timedelta(hours=2, minutes=30),
            "assigned_at": now - timedelta(hours=2),
            "collected_at": now - timedelta(hours=1),
            "completed_at": None,
        },
        {
            "code": "PR-08",
            "batch_code": "FB-14",
            "ngo_email": "pragati_trust@example.com",
            "volunteer_email": "ananya_volunteer@example.com",
            "request_status": "collected",
            "requested_at": now - timedelta(hours=3),
            "assigned_at": now - timedelta(hours=2, minutes=15),
            "collected_at": now - timedelta(hours=1, minutes=15),
            "completed_at": None,
        },
        {
            "code": "PR-09",
            "batch_code": "FB-15",
            "ngo_email": "sneha_mandir@example.com",
            "volunteer_email": "vikram_volunteer@example.com",
            "request_status": "collected",
            "requested_at": now - timedelta(hours=4),
            "assigned_at": now - timedelta(hours=3),
            "collected_at": now - timedelta(hours=1, minutes=45),
            "completed_at": None,
        },

        # --- DELIVERED (3) ---
        {
            "code": "PR-10",
            "batch_code": "FB-16",
            "ngo_email": "care_foundation@example.com",
            "volunteer_email": "alex_volunteer@example.com",
            "request_status": "delivered",
            "requested_at": now - timedelta(hours=23),
            "assigned_at": now - timedelta(hours=22),
            "collected_at": now - timedelta(hours=21),
            "completed_at": now - timedelta(hours=20),
        },
        {
            "code": "PR-11",
            "batch_code": "FB-17",
            "ngo_email": "st_anthony_home@example.com",
            "volunteer_email": "priya_volunteer@example.com",
            "request_status": "delivered",
            "requested_at": now - timedelta(hours=25),
            "assigned_at": now - timedelta(hours=24),
            "collected_at": now - timedelta(hours=23),
            "completed_at": now - timedelta(hours=22),
        },
        {
            "code": "PR-12",
            "batch_code": "FB-18",
            "ngo_email": "pragati_trust@example.com",
            "volunteer_email": "neha_volunteer@example.com",
            "request_status": "delivered",
            "requested_at": now - timedelta(hours=28),
            "assigned_at": now - timedelta(hours=27),
            "collected_at": now - timedelta(hours=26),
            "completed_at": now - timedelta(hours=25),
        },

        # --- CANCELLED (3) ---
        {
            "code": "PR-13",
            "batch_code": "FB-19",
            "ngo_email": "feed_all@example.com",
            "volunteer_email": None,
            "request_status": "cancelled",
            "requested_at": now - timedelta(hours=12),
            "assigned_at": None,
            "collected_at": None,
            "completed_at": None,
        },
        {
            "code": "PR-14",
            "batch_code": "FB-20",
            "ngo_email": "sneha_mandir@example.com",
            "volunteer_email": None,
            "request_status": "cancelled",
            "requested_at": now - timedelta(hours=8),
            "assigned_at": None,
            "collected_at": None,
            "completed_at": None,
        },
        {
            "code": "PR-15",
            "batch_code": "FB-01",  # Historical cancelled request for FB-01, leaving FB-01 currently available!
            "ngo_email": "pragati_trust@example.com",
            "volunteer_email": None,
            "request_status": "cancelled",
            "requested_at": now - timedelta(hours=2),
            "assigned_at": None,
            "collected_at": None,
            "completed_at": None,
        },
    ]

# -----------------------------------------------------------------------------
# 4. DELIVERY LOGS DEFINITIONS (36 Total)
# -----------------------------------------------------------------------------

def get_synthetic_delivery_logs(req_map: dict, user_map: dict, req_def_map: dict):
    logs = []
    
    # Helper to append log
    def add_log(req_code, user_email, action, notes, logged_at):
        logs.append({
            "req_code": req_code,
            "user_email": user_email,
            "action": action,
            "notes": notes,
            "logged_at": logged_at,
        })

    # PR-01 (requested)
    r1 = req_def_map["PR-01"]
    add_log("PR-01", r1["ngo_email"], "FOOD_REQUESTED", "Care & Hope Shelter requested this batch for evening food distribution.", r1["requested_at"])

    # PR-02 (requested)
    r2 = req_def_map["PR-02"]
    add_log("PR-02", r2["ngo_email"], "FOOD_REQUESTED", "Feed The Hungry Mission requested Paneer Butter Masala for homeless kitchen.", r2["requested_at"])

    # PR-03 (requested)
    r3 = req_def_map["PR-03"]
    add_log("PR-03", r3["ngo_email"], "FOOD_REQUESTED", "St. Anthony's Children's Home requested South Indian Tiffin meals.", r3["requested_at"])

    # PR-04 (assigned)
    r4 = req_def_map["PR-04"]
    add_log("PR-04", r4["ngo_email"], "FOOD_REQUESTED", "Requested Chicken Cafreal meal batch from Ritz Classic.", r4["requested_at"])
    add_log("PR-04", r4["volunteer_email"], "PICKUP_ASSIGNED", "Volunteer Alex accepted pickup assignment; dispatched to Panaji venue.", r4["assigned_at"])

    # PR-05 (assigned)
    r5 = req_def_map["PR-05"]
    add_log("PR-05", r5["ngo_email"], "FOOD_REQUESTED", "Requested Vegetable Dum Biryani for dinner service.", r5["requested_at"])
    add_log("PR-05", r5["volunteer_email"], "PICKUP_ASSIGNED", "Volunteer Priya claimed pickup assignment.", r5["assigned_at"])

    # PR-06 (assigned)
    r6 = req_def_map["PR-06"]
    add_log("PR-06", r6["ngo_email"], "FOOD_REQUESTED", "Requested Banana Walnut Bread from Bakers Street.", r6["requested_at"])
    add_log("PR-06", r6["volunteer_email"], "PICKUP_ASSIGNED", "Volunteer Rohan claimed pickup assignment from Porvorim.", r6["assigned_at"])

    # PR-07 (collected)
    r7 = req_def_map["PR-07"]
    add_log("PR-07", r7["ngo_email"], "FOOD_REQUESTED", "Requested Whole Wheat Chapatis from campus mess.", r7["requested_at"])
    add_log("PR-07", r7["volunteer_email"], "PICKUP_ASSIGNED", "Volunteer Alex Rivera accepted pickup assignment.", r7["assigned_at"])
    add_log("PR-07", r7["volunteer_email"], "FOOD_COLLECTED", "Collected 50 servings in insulated warm containers from Goa Univ Mess.", r7["collected_at"])

    # PR-08 (collected)
    r8 = req_def_map["PR-08"]
    add_log("PR-08", r8["ngo_email"], "FOOD_REQUESTED", "Requested Continental Buffet Trays from Grand Hyatt Kitchen.", r8["requested_at"])
    add_log("PR-08", r8["volunteer_email"], "PICKUP_ASSIGNED", "Volunteer Ananya Deshmukh accepted pickup.", r8["assigned_at"])
    add_log("PR-08", r8["volunteer_email"], "FOOD_COLLECTED", "Food verified fresh, packed into thermal delivery boxes, en route to Vasco.", r8["collected_at"])

    # PR-09 (collected)
    r9 = req_def_map["PR-09"]
    add_log("PR-09", r9["ngo_email"], "FOOD_REQUESTED", "Requested Farm Fresh Spinach & Greens from Green Bites.", r9["requested_at"])
    add_log("PR-09", r9["volunteer_email"], "PICKUP_ASSIGNED", "Volunteer Vikram Naik claimed pickup assignment.", r9["assigned_at"])
    add_log("PR-09", r9["volunteer_email"], "FOOD_COLLECTED", "Loaded 15 kg washed produce at Miramar cafe; en route to Ponda.", r9["collected_at"])

    # PR-10 (delivered)
    r10 = req_def_map["PR-10"]
    add_log("PR-10", r10["ngo_email"], "FOOD_REQUESTED", "Requested Goan Fish Thali Box Meals.", r10["requested_at"])
    add_log("PR-10", r10["volunteer_email"], "PICKUP_ASSIGNED", "Volunteer Alex accepted pickup assignment.", r10["assigned_at"])
    add_log("PR-10", r10["volunteer_email"], "FOOD_COLLECTED", "Picked up sealed meal boxes from Ritz Classic Panaji.", r10["collected_at"])
    add_log("PR-10", r10["volunteer_email"], "DELIVERY_COMPLETED", "Delivered safely to Care & Hope Shelter Altinho. Staff confirmed 30 servings.", r10["completed_at"])

    # PR-11 (delivered)
    r11 = req_def_map["PR-11"]
    add_log("PR-11", r11["ngo_email"], "FOOD_REQUESTED", "Requested bakery surplus from Bakers Street.", r11["requested_at"])
    add_log("PR-11", r11["volunteer_email"], "PICKUP_ASSIGNED", "Volunteer Priya Sharma claimed pickup.", r11["assigned_at"])
    add_log("PR-11", r11["volunteer_email"], "FOOD_COLLECTED", "Collected 16 kg croissants and sweet buns from Porvorim bakery.", r11["collected_at"])
    add_log("PR-11", r11["volunteer_email"], "DELIVERY_COMPLETED", "Delivered to St. Anthony's Home Mapusa in good condition.", r11["completed_at"])

    # PR-12 (delivered)
    r12 = req_def_map["PR-12"]
    add_log("PR-12", r12["ngo_email"], "FOOD_REQUESTED", "Requested 55 servings Comfort Moong Dal Khichdi from Spice Goa.", r12["requested_at"])
    add_log("PR-12", r12["volunteer_email"], "PICKUP_ASSIGNED", "Volunteer Neha Kamat claimed pickup.", r12["assigned_at"])
    add_log("PR-12", r12["volunteer_email"], "FOOD_COLLECTED", "Collected warm food vessels from Mapusa kitchen.", r12["collected_at"])
    add_log("PR-12", r12["volunteer_email"], "DELIVERY_COMPLETED", "Delivered to Pragati Community Kitchen Vasco. Hot meals served immediately.", r12["completed_at"])

    # PR-13 (cancelled - expired)
    r13 = req_def_map["PR-13"]
    add_log("PR-13", r13["ngo_email"], "FOOD_REQUESTED", "Requested Cooked Rajma Masala from campus mess.", r13["requested_at"])
    add_log("PR-13", None, "DONATION_EXPIRED", "Batch passed expiry time before volunteer pickup could be dispatched. System auto-cancelled request.", r13["requested_at"] + timedelta(hours=6))

    # PR-14 (cancelled - expired)
    r14 = req_def_map["PR-14"]
    add_log("PR-14", r14["ngo_email"], "FOOD_REQUESTED", "Requested Vegetable Samosas for community snack.", r14["requested_at"])
    add_log("PR-14", None, "DONATION_EXPIRED", "Donation expired before volunteer assignment. System marked cancelled.", r14["requested_at"] + timedelta(hours=4))

    # PR-15 (cancelled - surplus returned to pool)
    r15 = req_def_map["PR-15"]
    add_log("PR-15", r15["ngo_email"], "FOOD_REQUESTED", "Requested Vegetable Pulao batch.", r15["requested_at"])
    add_log("PR-15", r15["ngo_email"], "REQUEST_CANCELLED", "Pragati Community Kitchen cancelled request due to local pantry surplus; batch returned to available network pool.", r15["requested_at"] + timedelta(minutes=40))

    return logs

# -----------------------------------------------------------------------------
# 5. NOTIFICATIONS DEFINITIONS (25 Total)
# -----------------------------------------------------------------------------

def get_synthetic_notifications(now: datetime):
    return [
        # --- DONOR NOTIFICATIONS (8) ---
        {
            "user_email": "green_bites@example.com",
            "title": "Donation Listed Successfully",
            "message": "Your donation 'Vegetable Pulao & Cucumber Raita' (40 servings) is now available for local NGOs.",
            "is_read": True,
            "created_at": now - timedelta(hours=2),
        },
        {
            "user_email": "green_bites@example.com",
            "title": "Pickup Request Received",
            "message": "Care & Hope Shelter Home has requested your donation 'Fresh Vegetable Club Sandwiches'.",
            "is_read": False,
            "created_at": now - timedelta(minutes=45),
        },
        {
            "user_email": "grand_hyatt_kitchen@example.com",
            "title": "Food Picked Up by Volunteer",
            "message": "Volunteer Ananya Deshmukh has collected 'Continental Banquet Buffet Trays' from your premises.",
            "is_read": False,
            "created_at": now - timedelta(hours=1, minutes=15),
        },
        {
            "user_email": "ritz_classic@example.com",
            "title": "Delivery Completed!",
            "message": "Thank you! 30 servings of 'Goan Fish Thali Box Meals' have been delivered to Care & Hope Shelter.",
            "is_read": True,
            "created_at": now - timedelta(hours=20),
        },
        {
            "user_email": "bakers_street@example.com",
            "title": "Delivery Completed!",
            "message": "16 kg 'Assorted Croissants & Sweet Buns' successfully delivered to St. Anthony's Children's Home.",
            "is_read": True,
            "created_at": now - timedelta(hours=22),
        },
        {
            "user_email": "spice_goa@example.com",
            "title": "Volunteer Dispatched",
            "message": "Volunteer Priya Sharma has been assigned to pick up 'Vegetable Dum Biryani & Mirchi Salan'.",
            "is_read": True,
            "created_at": now - timedelta(hours=1, minutes=15),
        },
        {
            "user_email": "campus_mess@example.com",
            "title": "Donation Expired Notice",
            "message": "Your listing 'Cooked Rajma Masala & Jeera Rice' has expired and is no longer visible to NGOs.",
            "is_read": True,
            "created_at": now - timedelta(hours=6),
        },
        {
            "user_email": "green_bites@example.com",
            "title": "Donation Expired Notice",
            "message": "Your listing 'Vegetable Samosas & Mint Chutney' reached its expiry time and has been marked Expired.",
            "is_read": True,
            "created_at": now - timedelta(hours=4),
        },

        # --- NGO NOTIFICATIONS (9) ---
        {
            "user_email": "care_foundation@example.com",
            "title": "Request Confirmed",
            "message": "Your request for 'Fresh Vegetable Club Sandwiches' is active and pending volunteer claim.",
            "is_read": False,
            "created_at": now - timedelta(minutes=45),
        },
        {
            "user_email": "feed_all@example.com",
            "title": "Request Broadcast to Volunteers",
            "message": "Your request for 'Paneer Butter Masala & Phulkas' is visible to nearby volunteers in Goa.",
            "is_read": False,
            "created_at": now - timedelta(minutes=30),
        },
        {
            "user_email": "st_anthony_home@example.com",
            "title": "Volunteer Assigned",
            "message": "Volunteer Priya Sharma has accepted your pickup request for 'Vegetable Dum Biryani & Mirchi Salan'.",
            "is_read": False,
            "created_at": now - timedelta(hours=1, minutes=15),
        },
        {
            "user_email": "care_foundation@example.com",
            "title": "Volunteer Dispatched",
            "message": "Volunteer Alex Rivera is on the way to pick up 'Cooked Chicken Cafreal & Butter Pav'.",
            "is_read": True,
            "created_at": now - timedelta(hours=1, minutes=30),
        },
        {
            "user_email": "pragati_trust@example.com",
            "title": "Food In Transit",
            "message": "Volunteer Ananya Deshmukh has collected 'Continental Banquet Buffet Trays' and is en route to Vasco.",
            "is_read": False,
            "created_at": now - timedelta(hours=1, minutes=15),
        },
        {
            "user_email": "feed_all@example.com",
            "title": "Food In Transit",
            "message": "Volunteer Alex Rivera collected 'Whole Wheat Chapatis & Aloo Gobi Dry' from Goa University Mess.",
            "is_read": True,
            "created_at": now - timedelta(hours=1),
        },
        {
            "user_email": "care_foundation@example.com",
            "title": "Delivery Arrived",
            "message": "30 servings of 'Goan Fish Thali Box Meals' were delivered to your facility.",
            "is_read": True,
            "created_at": now - timedelta(hours=20),
        },
        {
            "user_email": "st_anthony_home@example.com",
            "title": "Delivery Arrived",
            "message": "16 kg bakery goods delivered by Volunteer Priya Sharma.",
            "is_read": True,
            "created_at": now - timedelta(hours=22),
        },
        {
            "user_email": "feed_all@example.com",
            "title": "Donation Request Expired",
            "message": "Requested batch 'Cooked Rajma Masala & Jeera Rice' reached expiry before pickup and was cancelled.",
            "is_read": True,
            "created_at": now - timedelta(hours=6),
        },

        # --- VOLUNTEER NOTIFICATIONS (8) ---
        {
            "user_email": "alex_volunteer@example.com",
            "title": "Urgent Rescue Available in Panaji",
            "message": "Vegetable Pulao & Cucumber Raita is expiring in under 2 hours! Claim pickup now to prevent food waste.",
            "is_read": False,
            "created_at": now - timedelta(hours=1),
        },
        {
            "user_email": "alex_volunteer@example.com",
            "title": "Pickup Task Assigned",
            "message": "You are assigned to collect 'Cooked Chicken Cafreal & Butter Pav' from Ritz Classic Seafood Restaurant.",
            "is_read": True,
            "created_at": now - timedelta(hours=1, minutes=30),
        },
        {
            "user_email": "priya_volunteer@example.com",
            "title": "Pickup Task Assigned",
            "message": "You are assigned to collect 'Vegetable Dum Biryani & Mirchi Salan' from Spice Goa Caterers Mapusa.",
            "is_read": True,
            "created_at": now - timedelta(hours=1, minutes=15),
        },
        {
            "user_email": "rohan_volunteer@example.com",
            "title": "Pickup Task Assigned",
            "message": "You claimed pickup of 'Banana Walnut Bread & Tea Cakes' from Bakers Street Porvorim.",
            "is_read": False,
            "created_at": now - timedelta(hours=1, minutes=40),
        },
        {
            "user_email": "ananya_volunteer@example.com",
            "title": "Food Transit Confirmation",
            "message": "Food collected. Please deliver to Pragati Community Welfare Center, Swatantra Path, Vasco.",
            "is_read": False,
            "created_at": now - timedelta(hours=1, minutes=15),
        },
        {
            "user_email": "vikram_volunteer@example.com",
            "title": "Food Transit Confirmation",
            "message": "Produce collected from Green Bites. Please deliver to Sneha Mandir Elderly Care, Bandora, Ponda.",
            "is_read": False,
            "created_at": now - timedelta(hours=1, minutes=45),
        },
        {
            "user_email": "alex_volunteer@example.com",
            "title": "Delivery Impact Recognized",
            "message": "Great job! Your delivery of Goan Fish Thali to Care & Hope Shelter was recorded in your impact log.",
            "is_read": True,
            "created_at": now - timedelta(hours=20),
        },
        {
            "user_email": "priya_volunteer@example.com",
            "title": "Delivery Impact Recognized",
            "message": "Great job! 16 kg of artisan bakery products safely delivered to St. Anthony's Children's Home.",
            "is_read": True,
            "created_at": now - timedelta(hours=22),
        },
    ]

# -----------------------------------------------------------------------------
# SEED EXECUTION LOGIC (Idempotent Upsert & Clean)
# -----------------------------------------------------------------------------

def seed_synthetic_data(reset: bool = False):
    db = SessionLocal()
    now = datetime.utcnow()
    pwd_hash = hash_password(DEFAULT_PASSWORD)

    stats = {
        "users_created": 0,
        "users_existing": 0,
        "donors_created": 0,
        "donors_updated": 0,
        "ngos_created": 0,
        "ngos_updated": 0,
        "volunteers_created": 0,
        "volunteers_updated": 0,
        "batches_created": 0,
        "batches_updated": 0,
        "requests_created": 0,
        "requests_updated": 0,
        "logs_created": 0,
        "logs_skipped": 0,
        "notifs_created": 0,
        "notifs_skipped": 0,
    }

    try:
        print("=" * 70)
        print("  COMMUNITY FOOD RESCUE NETWORK - SYNTHETIC DATA SEEDER")
        print("=" * 70)
        print(f"[*] Target Location: Goa, India")
        print(f"[*] Base UTC Reference Time: {now.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print(f"[*] Default Demo Credentials Password: '{DEFAULT_PASSWORD}'\n")

        # ---------------------------------------------------------------------
        # STEP 1: SEED USERS & PROFILES (6 Donors, 5 NGOs, 9 Volunteers = 20)
        # ---------------------------------------------------------------------
        print("[1/5] Processing 20 Synthetic Users & Role Profiles...")
        users_by_email = {}
        donors_by_email = {}
        ngos_by_email = {}
        volunteers_by_email = {}

        # 1A. Donors (6)
        for d_info in SYNTHETIC_DONORS:
            user = db.query(User).filter(User.email == d_info["email"]).first()
            if not user:
                user = User(
                    name=d_info["name"],
                    email=d_info["email"],
                    password_hash=pwd_hash,
                    role="donor",
                    is_active=True,
                    created_at=now - timedelta(days=30),
                    updated_at=now,
                )
                db.add(user)
                db.flush()
                stats["users_created"] += 1
            else:
                user.name = d_info["name"]
                user.is_active = True
                stats["users_existing"] += 1
            users_by_email[d_info["email"]] = user

            # Profile
            donor = db.query(Donor).filter(Donor.user_id == user.user_id).first()
            if not donor:
                donor = Donor(
                    user_id=user.user_id,
                    donor_name=d_info["donor_name"],
                    phone=d_info["phone"],
                    address=d_info["address"],
                    latitude=d_info["latitude"],
                    longitude=d_info["longitude"],
                )
                db.add(donor)
                db.flush()
                stats["donors_created"] += 1
            else:
                donor.donor_name = d_info["donor_name"]
                donor.phone = d_info["phone"]
                donor.address = d_info["address"]
                donor.latitude = d_info["latitude"]
                donor.longitude = d_info["longitude"]
                stats["donors_updated"] += 1
            donors_by_email[d_info["email"]] = donor

        # 1B. NGOs (5)
        for n_info in SYNTHETIC_NGOS:
            user = db.query(User).filter(User.email == n_info["email"]).first()
            if not user:
                user = User(
                    name=n_info["name"],
                    email=n_info["email"],
                    password_hash=pwd_hash,
                    role="ngo",
                    is_active=True,
                    created_at=now - timedelta(days=30),
                    updated_at=now,
                )
                db.add(user)
                db.flush()
                stats["users_created"] += 1
            else:
                user.name = n_info["name"]
                user.is_active = True
                stats["users_existing"] += 1
            users_by_email[n_info["email"]] = user

            # Profile
            ngo = db.query(NGOPartner).filter(NGOPartner.user_id == user.user_id).first()
            if not ngo:
                ngo = NGOPartner(
                    user_id=user.user_id,
                    ngo_name=n_info["ngo_name"],
                    phone=n_info["phone"],
                    address=n_info["address"],
                    latitude=n_info["latitude"],
                    longitude=n_info["longitude"],
                )
                db.add(ngo)
                db.flush()
                stats["ngos_created"] += 1
            else:
                ngo.ngo_name = n_info["ngo_name"]
                ngo.phone = n_info["phone"]
                ngo.address = n_info["address"]
                ngo.latitude = n_info["latitude"]
                ngo.longitude = n_info["longitude"]
                stats["ngos_updated"] += 1
            ngos_by_email[n_info["email"]] = ngo

        # 1C. Volunteers (9)
        for v_info in SYNTHETIC_VOLUNTEERS:
            user = db.query(User).filter(User.email == v_info["email"]).first()
            if not user:
                user = User(
                    name=v_info["name"],
                    email=v_info["email"],
                    password_hash=pwd_hash,
                    role="volunteer",
                    is_active=True,
                    created_at=now - timedelta(days=30),
                    updated_at=now,
                )
                db.add(user)
                db.flush()
                stats["users_created"] += 1
            else:
                user.name = v_info["name"]
                user.is_active = True
                stats["users_existing"] += 1
            users_by_email[v_info["email"]] = user

            # Profile
            vol = db.query(Volunteer).filter(Volunteer.user_id == user.user_id).first()
            if not vol:
                vol = Volunteer(
                    user_id=user.user_id,
                    volunteer_name=v_info["volunteer_name"],
                    phone=v_info["phone"],
                    availability_status=v_info["availability_status"],
                    created_at=now - timedelta(days=30),
                )
                db.add(vol)
                db.flush()
                stats["volunteers_created"] += 1
            else:
                vol.volunteer_name = v_info["volunteer_name"]
                vol.phone = v_info["phone"]
                vol.availability_status = v_info["availability_status"]
                stats["volunteers_updated"] += 1
            volunteers_by_email[v_info["email"]] = vol

        db.flush()
        print(f"    -> Users: {stats['users_created']} created, {stats['users_existing']} existing/verified.")
        print(f"    -> Donors: {stats['donors_created']} created, {stats['donors_updated']} updated.")
        print(f"    -> NGOs: {stats['ngos_created']} created, {stats['ngos_updated']} updated.")
        print(f"    -> Volunteers: {stats['volunteers_created']} created, {stats['volunteers_updated']} updated.")

        # ---------------------------------------------------------------------
        # STEP 2: SEED FOOD BATCHES (20 Batches)
        # ---------------------------------------------------------------------
        print("\n[2/5] Processing 20 Food Batches (Varied Categories & Expiring Offsets)...")
        batches_def = get_synthetic_food_batches(now, donors_by_email)
        batches_by_code = {}

        for b_info in batches_def:
            donor = donors_by_email[b_info["donor_email"]]
            # Match existing batch by donor_id and food_name
            batch = (
                db.query(FoodBatch)
                .filter(FoodBatch.donor_id == donor.donor_id, FoodBatch.food_name == b_info["food_name"])
                .first()
            )

            if not batch:
                batch = FoodBatch(
                    donor_id=donor.donor_id,
                    food_name=b_info["food_name"],
                    food_category=b_info["food_category"],
                    quantity=b_info["quantity"],
                    unit=b_info["unit"],
                    prepared_at=b_info["prepared_at"],
                    expiry_time=b_info["expiry_time"],
                    food_status=b_info["food_status"],
                    pickup_address=donor.address,
                    latitude=donor.latitude,
                    longitude=donor.longitude,
                    created_at=b_info["prepared_at"],
                    updated_at=now,
                )
                db.add(batch)
                db.flush()
                stats["batches_created"] += 1
            else:
                # Update relative timestamps so demo data stays realistic relative to run time
                batch.food_category = b_info["food_category"]
                batch.quantity = b_info["quantity"]
                batch.unit = b_info["unit"]
                batch.prepared_at = b_info["prepared_at"]
                batch.expiry_time = b_info["expiry_time"]
                batch.food_status = b_info["food_status"]
                batch.pickup_address = donor.address
                batch.latitude = donor.latitude
                batch.longitude = donor.longitude
                batch.updated_at = now
                stats["batches_updated"] += 1

            batches_by_code[b_info["code"]] = batch

        db.flush()
        print(f"    -> Food Batches: {stats['batches_created']} created, {stats['batches_updated']} refreshed.")

        # ---------------------------------------------------------------------
        # STEP 3: SEED PICKUP REQUESTS (15 Requests)
        # ---------------------------------------------------------------------
        print("\n[3/5] Processing 15 Pickup Requests (Complete Relational Pipeline)...")
        requests_def = get_synthetic_pickup_requests(now)
        req_def_map = {r["code"]: r for r in requests_def}
        requests_by_code = {}

        for r_info in requests_def:
            batch = batches_by_code[r_info["batch_code"]]
            ngo = ngos_by_email[r_info["ngo_email"]]
            vol = volunteers_by_email[r_info["volunteer_email"]] if r_info["volunteer_email"] else None

            # Look for existing request for this batch and NGO
            request = (
                db.query(PickupRequest)
                .filter(PickupRequest.batch_id == batch.batch_id, PickupRequest.ngo_id == ngo.ngo_id)
                .first()
            )

            if not request:
                request = PickupRequest(
                    batch_id=batch.batch_id,
                    ngo_id=ngo.ngo_id,
                    volunteer_id=vol.volunteer_id if vol else None,
                    request_status=r_info["request_status"],
                    requested_at=r_info["requested_at"],
                    assigned_at=r_info["assigned_at"],
                    collected_at=r_info["collected_at"],
                    completed_at=r_info["completed_at"],
                    updated_at=now,
                )
                db.add(request)
                db.flush()
                stats["requests_created"] += 1
            else:
                request.volunteer_id = vol.volunteer_id if vol else None
                request.request_status = r_info["request_status"]
                request.requested_at = r_info["requested_at"]
                request.assigned_at = r_info["assigned_at"]
                request.collected_at = r_info["collected_at"]
                request.completed_at = r_info["completed_at"]
                request.updated_at = now
                stats["requests_updated"] += 1

            requests_by_code[r_info["code"]] = request

        db.flush()
        print(f"    -> Pickup Requests: {stats['requests_created']} created, {stats['requests_updated']} refreshed.")

        # ---------------------------------------------------------------------
        # STEP 4: SEED DELIVERY LOGS (36 Logs)
        # ---------------------------------------------------------------------
        print("\n[4/5] Processing 36 Audit Delivery Logs...")
        logs_def = get_synthetic_delivery_logs(requests_by_code, users_by_email, req_def_map)

        for l_info in logs_def:
            req = requests_by_code[l_info["req_code"]]
            user = users_by_email[l_info["user_email"]] if l_info["user_email"] else None

            # Check if this exact action already exists for this request
            existing_log = (
                db.query(DeliveryLog)
                .filter(DeliveryLog.request_id == req.request_id, DeliveryLog.action == l_info["action"])
                .first()
            )

            if not existing_log:
                log = DeliveryLog(
                    request_id=req.request_id,
                    performed_by_user_id=user.user_id if user else None,
                    action=l_info["action"],
                    notes=l_info["notes"],
                    logged_at=l_info["logged_at"],
                )
                db.add(log)
                stats["logs_created"] += 1
            else:
                stats["logs_skipped"] += 1

        db.flush()
        print(f"    -> Delivery Logs: {stats['logs_created']} created, {stats['logs_skipped']} existing/skipped.")

        # ---------------------------------------------------------------------
        # STEP 5: SEED NOTIFICATIONS (25 Notifications)
        # ---------------------------------------------------------------------
        print("\n[5/5] Processing 25 In-App Role Notifications...")
        notifs_def = get_synthetic_notifications(now)

        for n_info in notifs_def:
            user = users_by_email[n_info["user_email"]]

            existing_notif = (
                db.query(Notification)
                .filter(Notification.user_id == user.user_id, Notification.title == n_info["title"])
                .first()
            )

            if not existing_notif:
                notif = Notification(
                    user_id=user.user_id,
                    title=n_info["title"],
                    message=n_info["message"],
                    is_read=n_info["is_read"],
                    created_at=n_info["created_at"],
                )
                db.add(notif)
                stats["notifs_created"] += 1
            else:
                stats["notifs_skipped"] += 1

        db.commit()
        print(f"    -> Notifications: {stats['notifs_created']} created, {stats['notifs_skipped']} existing/skipped.")

        print("\n" + "=" * 70)
        print("  SYNTHETIC DATA SEEDING COMPLETE [SUCCESS]")
        print("=" * 70)
        print("  Summary of Operations:")
        for k, v in stats.items():
            print(f"    - {k:<22}: {v}")
        print("=" * 70 + "\n")

    except Exception as e:
        db.rollback()
        print(f"\n[FATAL ERROR] Seeding aborted and rolled back cleanly: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


def clean_synthetic_data():
    """
    Safely removes only the synthetic demo data (identified by known synthetic emails),
    preserving any non-synthetic or user-created records.
    """
    db = SessionLocal()
    try:
        print("[Clean] Searching for synthetic demo accounts to remove...")
        synth_users = db.query(User).filter(User.email.in_(ALL_SYNTHETIC_EMAILS)).all()
        if not synth_users:
            print("[Clean] No synthetic demo users found. Nothing to remove.")
            return

        user_ids = [u.user_id for u in synth_users]
        print(f"[Clean] Found {len(synth_users)} synthetic user records to delete (Cascade deletes linked profiles, batches, requests, logs, notifications).")

        for u in synth_users:
            db.delete(u)

        db.commit()
        print("[Clean] Synthetic demo records cleaned successfully!")
    except Exception as e:
        db.rollback()
        print(f"[Clean Error] Failed to clean synthetic data: {e}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed synthetic data for Community Food Rescue Network.")
    parser.add_argument("--clean", action="store_true", help="Remove only the synthetic demo data from MySQL.")
    parser.add_argument("--refresh", action="store_true", help="Clean and re-seed fresh synthetic data.")
    args = parser.parse_args()

    if args.clean:
        clean_synthetic_data()
    elif args.refresh:
        clean_synthetic_data()
        seed_synthetic_data()
    else:
        seed_synthetic_data()
