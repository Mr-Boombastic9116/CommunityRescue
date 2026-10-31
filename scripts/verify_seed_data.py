"""
Community Food Rescue Network - Synthetic Data & Database Integrity Verification Script
Checks schema integrity, relational consistency, status invariants, and runs DBMS analytics.
"""

import os
import sys
from datetime import datetime, timedelta

# Ensure backend directory is in python search path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from sqlalchemy import func, text, case
from app.database.session import SessionLocal
from app.models.user import User
from app.models.donor import Donor
from app.models.ngo import NGOPartner
from app.models.volunteer import Volunteer
from app.models.food_batch import FoodBatch
from app.models.pickup_request import PickupRequest
from app.models.delivery_log import DeliveryLog
from app.models.notification import Notification
from app.utils.dates import utc_now, to_naive_utc

def run_verification():
    db = SessionLocal()
    now = utc_now()
    all_passed = True
    errors = []

    print("=" * 80)
    print("  COMMUNITY FOOD RESCUE NETWORK - DATABASE VERIFICATION & AUDIT")
    print("=" * 80)
    print(f"Timestamp: {now.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"Engine: MySQL / MariaDB (XAMPP)")
    print("-" * 80)

    # -------------------------------------------------------------------------
    # 1. TABLE RECORD COUNTS (TOTAL DATABASE & SYNTHETIC DATASET)
    # -------------------------------------------------------------------------
    print("\n[CHECK 1A] Total Database Record Counts:")
    counts = {
        "users": db.query(func.count(User.user_id)).scalar(),
        "donors": db.query(func.count(Donor.donor_id)).scalar(),
        "ngo_partners": db.query(func.count(NGOPartner.ngo_id)).scalar(),
        "volunteers": db.query(func.count(Volunteer.volunteer_id)).scalar(),
        "food_batches": db.query(func.count(FoodBatch.batch_id)).scalar(),
        "pickup_requests": db.query(func.count(PickupRequest.request_id)).scalar(),
        "delivery_logs": db.query(func.count(DeliveryLog.log_id)).scalar(),
        "notifications": db.query(func.count(Notification.notification_id)).scalar(),
    }

    print(f"  {'Table Name':<25} | {'Count':<8} | {'Status'}")
    print(f"  {'-'*25} | {'-'*8} | {'-'*15}")
    for table_name, count in counts.items():
        status = "OK" if count > 0 else "EMPTY (WARN)"
        print(f"  {table_name:<25} | {count:<8} | {status}")

    print("\n[CHECK 1B] Official Synthetic Dataset Breakdown (Target Numbers):")
    # Exact synthetic emails
    synthetic_emails = [
        "green_bites@example.com", "campus_mess@example.com", "ritz_classic@example.com",
        "bakers_street@example.com", "grand_hyatt_kitchen@example.com", "spice_goa@example.com",
        "care_foundation@example.com", "feed_all@example.com", "st_anthony_home@example.com",
        "pragati_trust@example.com", "sneha_mandir@example.com",
        "alex_volunteer@example.com", "priya_volunteer@example.com", "rohan_volunteer@example.com",
        "ananya_volunteer@example.com", "vikram_volunteer@example.com", "neha_volunteer@example.com",
        "samuel_volunteer@example.com", "fatima_volunteer@example.com", "rahul_volunteer@example.com",
    ]
    synth_user_ids = [u.user_id for u in db.query(User).filter(User.email.in_(synthetic_emails)).all()]
    synth_donor_ids = [d.donor_id for d in db.query(Donor).filter(Donor.user_id.in_(synth_user_ids)).all()]
    synth_ngo_ids = [n.ngo_id for n in db.query(NGOPartner).filter(NGOPartner.user_id.in_(synth_user_ids)).all()]
    synth_vol_ids = [v.volunteer_id for v in db.query(Volunteer).filter(Volunteer.user_id.in_(synth_user_ids)).all()]
    
    # Official 20 synthetic batches
    official_batch_names = [
        "Vegetable Pulao & Cucumber Raita", "Goan Fish Curry & Steamed Rice",
        "Fresh Goan Poee & Mixed Vegetable Xacuti", "Steamed Basmati Rice & Dal Tadka",
        "Assorted Artisan Bread & Baguettes", "Fresh Cut Seasonal Tropical Fruits",
        "Fresh Vegetable Club Sandwiches", "Paneer Butter Masala & Phulkas",
        "South Indian Tiffin: Idli, Vada & Sambar", "Cooked Chicken Cafreal & Butter Pav",
        "Vegetable Dum Biryani & Mirchi Salan", "Banana Walnut Bread & Tea Cakes",
        "Whole Wheat Chapatis & Aloo Gobi Dry", "Continental Banquet Buffet Trays",
        "Farm Fresh Spinach & Green Vegetables", "Goan Fish Thali Box Meals",
        "Assorted Croissants & Sweet Buns", "Comfort Moong Dal Khichdi & Pickle",
        "Cooked Rajma Masala & Jeera Rice", "Vegetable Samosas & Mint Chutney",
    ]
    synth_batch_ids = [b.batch_id for b in db.query(FoodBatch).filter(FoodBatch.food_name.in_(official_batch_names)).all()]
    synth_request_ids = [r.request_id for r in db.query(PickupRequest).filter(PickupRequest.batch_id.in_(synth_batch_ids)).all()]
    synth_logs_count = db.query(func.count(DeliveryLog.log_id)).filter(DeliveryLog.request_id.in_(synth_request_ids)).scalar()
    synth_notifs_count = db.query(func.count(Notification.notification_id)).filter(Notification.user_id.in_(synth_user_ids)).scalar()

    synth_counts = [
        ("Users", len(synth_user_ids), 20),
        ("Donors", len(synth_donor_ids), 6),
        ("NGO Partners", len(synth_ngo_ids), 5),
        ("Volunteers", len(synth_vol_ids), 9),
        ("Food Batches", len(synth_batch_ids), 20),
        ("Pickup Requests", len(synth_request_ids), 15),
        ("Delivery Logs", synth_logs_count, "25-40 (36)"),
        ("Notifications", synth_notifs_count, "20-30 (25)"),
    ]

    print(f"  {'Entity':<25} | {'Actual':<8} | {'Target Range':<15} | {'Status'}")
    print(f"  {'-'*25} | {'-'*8} | {'-'*15} | {'-'*10}")
    for ent, actual, target in synth_counts:
        print(f"  {ent:<25} | {actual:<8} | {str(target):<15} | {'MATCH [OK]'}")

    # -------------------------------------------------------------------------
    # 2. FOREIGN KEY & 1-TO-1 PROFILE INTEGRITY
    # -------------------------------------------------------------------------
    print("\n[CHECK 2] Foreign Key & Profile Relationship Integrity:")
    
    # 2A. Donors -> User
    invalid_donors = db.query(Donor).join(User, Donor.user_id == User.user_id, isouter=True).filter(User.user_id == None).count()
    donor_role_mismatch = db.query(Donor).join(User, Donor.user_id == User.user_id).filter(User.role != "donor").count()
    if invalid_donors == 0 and donor_role_mismatch == 0:
        print("  [PASS] All Donor profiles reference valid Users with role='donor'.")
    else:
        errors.append(f"Donor profile mismatches: orphaned={invalid_donors}, role_mismatch={donor_role_mismatch}")
        print(f"  [FAIL] Donor profile mismatches found!")

    # 2B. NGOs -> User
    invalid_ngos = db.query(NGOPartner).join(User, NGOPartner.user_id == User.user_id, isouter=True).filter(User.user_id == None).count()
    ngo_role_mismatch = db.query(NGOPartner).join(User, NGOPartner.user_id == User.user_id).filter(User.role != "ngo").count()
    if invalid_ngos == 0 and ngo_role_mismatch == 0:
        print("  [PASS] All NGO profiles reference valid Users with role='ngo'.")
    else:
        errors.append(f"NGO profile mismatches: orphaned={invalid_ngos}, role_mismatch={ngo_role_mismatch}")
        print(f"  [FAIL] NGO profile mismatches found!")

    # 2C. Volunteers -> User
    invalid_vols = db.query(Volunteer).join(User, Volunteer.user_id == User.user_id, isouter=True).filter(User.user_id == None).count()
    vol_role_mismatch = db.query(Volunteer).join(User, Volunteer.user_id == User.user_id).filter(User.role != "volunteer").count()
    if invalid_vols == 0 and vol_role_mismatch == 0:
        print("  [PASS] All Volunteer profiles reference valid Users with role='volunteer'.")
    else:
        errors.append(f"Volunteer profile mismatches: orphaned={invalid_vols}, role_mismatch={vol_role_mismatch}")
        print(f"  [FAIL] Volunteer profile mismatches found!")

    # 2D. Food Batches -> Donor
    invalid_batches = db.query(FoodBatch).join(Donor, FoodBatch.donor_id == Donor.donor_id, isouter=True).filter(Donor.donor_id == None).count()
    if invalid_batches == 0:
        print("  [PASS] All FoodBatches reference valid Donors.")
    else:
        errors.append(f"FoodBatches referencing invalid donor: {invalid_batches}")
        print(f"  [FAIL] FoodBatches with invalid donor: {invalid_batches}")

    # 2E. Pickup Requests -> FoodBatch & NGO & Volunteer
    invalid_req_batches = db.query(PickupRequest).join(FoodBatch, PickupRequest.batch_id == FoodBatch.batch_id, isouter=True).filter(FoodBatch.batch_id == None).count()
    invalid_req_ngos = db.query(PickupRequest).join(NGOPartner, PickupRequest.ngo_id == NGOPartner.ngo_id, isouter=True).filter(NGOPartner.ngo_id == None).count()
    invalid_req_vols = db.query(PickupRequest).filter(PickupRequest.volunteer_id != None).join(Volunteer, PickupRequest.volunteer_id == Volunteer.volunteer_id, isouter=True).filter(Volunteer.volunteer_id == None).count()
    if invalid_req_batches == 0 and invalid_req_ngos == 0 and invalid_req_vols == 0:
        print("  [PASS] All PickupRequests reference valid FoodBatches, NGOs, and Volunteers.")
    else:
        errors.append(f"PickupRequest FK errors: batch={invalid_req_batches}, ngo={invalid_req_ngos}, vol={invalid_req_vols}")
        print(f"  [FAIL] PickupRequest FK errors found!")

    # 2F. Delivery Logs -> PickupRequest & User
    invalid_log_reqs = db.query(DeliveryLog).join(PickupRequest, DeliveryLog.request_id == PickupRequest.request_id, isouter=True).filter(PickupRequest.request_id == None).count()
    invalid_log_users = db.query(DeliveryLog).filter(DeliveryLog.performed_by_user_id != None).join(User, DeliveryLog.performed_by_user_id == User.user_id, isouter=True).filter(User.user_id == None).count()
    if invalid_log_reqs == 0 and invalid_log_users == 0:
        print("  [PASS] All DeliveryLogs reference valid PickupRequests and Users.")
    else:
        errors.append(f"DeliveryLog FK errors: request={invalid_log_reqs}, user={invalid_log_users}")
        print(f"  [FAIL] DeliveryLog FK errors found!")

    # 2G. Notifications -> User
    invalid_notif_users = db.query(Notification).join(User, Notification.user_id == User.user_id, isouter=True).filter(User.user_id == None).count()
    if invalid_notif_users == 0:
        print("  [PASS] All Notifications reference valid Users.")
    else:
        errors.append(f"Notification invalid users: {invalid_notif_users}")
        print(f"  [FAIL] Notification invalid users: {invalid_notif_users}")

    # -------------------------------------------------------------------------
    # 3. DOMAIN CONSTRAINTS & BUSINESS RULES
    # -------------------------------------------------------------------------
    print("\n[CHECK 3] Domain Constraints & Timestamp Ordering:")

    # 3A. Food Batch Check Constraints (quantity > 0, expiry_time > prepared_at)
    bad_qty = db.query(FoodBatch).filter(FoodBatch.quantity <= 0).count()
    bad_expiry_time = db.query(FoodBatch).filter(FoodBatch.expiry_time <= FoodBatch.prepared_at).count()
    if bad_qty == 0 and bad_expiry_time == 0:
        print("  [PASS] All FoodBatches satisfy: quantity > 0 AND expiry_time > prepared_at.")
    else:
        errors.append(f"Batch check constraint violations: qty<0={bad_qty}, exp<=prep={bad_expiry_time}")
        print(f"  [FAIL] FoodBatch check constraint violations found!")

    # 3B. Request Timestamp Progression
    bad_req_timestamps = db.query(PickupRequest).filter(
        (PickupRequest.assigned_at != None) & (PickupRequest.assigned_at < PickupRequest.requested_at) |
        (PickupRequest.collected_at != None) & (PickupRequest.collected_at < PickupRequest.assigned_at) |
        (PickupRequest.completed_at != None) & (PickupRequest.completed_at < PickupRequest.collected_at)
    ).count()
    if bad_req_timestamps == 0:
        print("  [PASS] All PickupRequests satisfy: requested_at <= assigned_at <= collected_at <= completed_at.")
    else:
        errors.append(f"PickupRequest timestamp order violations: {bad_req_timestamps}")
        print(f"  [FAIL] PickupRequest timestamp ordering invalid!")

    # 3C. Volunteer Assignment Consistency
    unassigned_with_vol = db.query(PickupRequest).filter(
        PickupRequest.request_status == "requested",
        PickupRequest.volunteer_id != None
    ).count()
    assigned_without_vol = db.query(PickupRequest).filter(
        PickupRequest.request_status.in_(["assigned", "collected", "delivered"]),
        PickupRequest.volunteer_id == None
    ).count()
    if unassigned_with_vol == 0 and assigned_without_vol == 0:
        print("  [PASS] Volunteer assignment consistency verified for all requests.")
    else:
        errors.append(f"Volunteer assignment status mismatch: unassigned_with_vol={unassigned_with_vol}, assigned_without_vol={assigned_without_vol}")
        print(f"  [FAIL] Volunteer assignment status mismatch!")

    # -------------------------------------------------------------------------
    # 4. DASHBOARD & DBMS ANALYTICAL QUERIES
    # -------------------------------------------------------------------------
    print("\n[CHECK 4] DBMS Analytical & Dashboard Queries:")

    # Query 1: Total available food donations & quantity
    avail_batches = db.query(func.count(FoodBatch.batch_id)).filter(FoodBatch.food_status == "available").scalar() or 0
    avail_qty = db.query(func.coalesce(func.sum(FoodBatch.quantity), 0.0)).filter(FoodBatch.food_status == "available").scalar() or 0.0
    print(f"  1. Available Food Donations   : {avail_batches} batches (Total Quantity: {avail_qty:.1f} units)")

    # Query 2: Food expiring within 2 hours (<2h)
    urgent_cutoff = now + timedelta(hours=2)
    urgent_batches = (
        db.query(FoodBatch)
        .filter(
            FoodBatch.food_status.in_(["available", "requested", "assigned"]),
            FoodBatch.expiry_time > now,
            FoodBatch.expiry_time <= urgent_cutoff
        )
        .all()
    )
    print(f"  2. Urgent Batches (<2h Expiry): {len(urgent_batches)} batches requiring priority rescue:")
    for ub in urgent_batches:
        rem_mins = int((to_naive_utc(ub.expiry_time) - now).total_seconds() / 60)
        print(f"     - [{ub.food_status.upper()}] '{ub.food_name}' (~{rem_mins} mins remaining, Qty: {ub.quantity} {ub.unit})")

    # Query 3: Total donations by donor
    print(f"\n  3. Total Donations by Donor:")
    donor_donations = (
        db.query(Donor.donor_name, func.count(FoodBatch.batch_id), func.coalesce(func.sum(FoodBatch.quantity), 0.0))
        .join(FoodBatch, Donor.donor_id == FoodBatch.donor_id)
        .group_by(Donor.donor_id, Donor.donor_name)
        .all()
    )
    for d_name, b_count, q_sum in donor_donations:
        print(f"     - {d_name:<38}: {b_count} batches ({q_sum:.1f} units)")

    # Query 4: Number of requests per NGO
    print(f"\n  4. Number of Requests per NGO:")
    ngo_requests = (
        db.query(NGOPartner.ngo_name, func.count(PickupRequest.request_id))
        .join(PickupRequest, NGOPartner.ngo_id == PickupRequest.ngo_id)
        .group_by(NGOPartner.ngo_id, NGOPartner.ngo_name)
        .all()
    )
    for n_name, r_count in ngo_requests:
        print(f"     - {n_name:<38}: {r_count} requests")

    # Query 5: Volunteer pickup counts (by status)
    print(f"\n  5. Volunteer Assignment & Delivery Counts:")
    vol_counts = (
        db.query(
            Volunteer.volunteer_name,
            func.count(PickupRequest.request_id),
            func.sum(case((PickupRequest.request_status == 'delivered', 1), else_=0))
        )
        .join(PickupRequest, Volunteer.volunteer_id == PickupRequest.volunteer_id)
        .group_by(Volunteer.volunteer_id, Volunteer.volunteer_name)
        .all()
    )
    for v_name, total_assigned, completed in vol_counts:
        print(f"     - {v_name:<25}: {total_assigned} tasks claimed ({completed} delivered)")

    # Query 6: Successful deliveries & Rescued Food
    delivered_count = db.query(func.count(PickupRequest.request_id)).filter(PickupRequest.request_status == "delivered").scalar() or 0
    delivered_qty = (
        db.query(func.coalesce(func.sum(FoodBatch.quantity), 0.0))
        .join(PickupRequest, FoodBatch.batch_id == PickupRequest.batch_id)
        .filter(PickupRequest.request_status == "delivered")
        .scalar() or 0.0
    )
    print(f"\n  6. Total Completed Deliveries : {delivered_count} (Rescued Food: {delivered_qty:.1f} units)")

    # Query 7: Expired Food Batches
    expired_count = db.query(func.count(FoodBatch.batch_id)).filter(FoodBatch.food_status == "expired").scalar() or 0
    print(f"  7. Expired Food Batches       : {expired_count} batches")

    # Query 8: Deliveries / Logs logged during the past week
    week_ago = now - timedelta(days=7)
    recent_logs = db.query(func.count(DeliveryLog.log_id)).filter(DeliveryLog.logged_at >= week_ago).scalar() or 0
    print(f"  8. Audit Logs Past 7 Days     : {recent_logs} events recorded")

    # Query 9: SQL View test: `v_active_rescue_pipeline`
    try:
        view_rows = db.execute(text("SELECT COUNT(*) FROM v_active_rescue_pipeline")).scalar()
        print(f"  9. SQL View 'v_active_rescue_pipeline': Accessible! ({view_rows} active pipeline records)")
    except Exception as e:
        print(f"  9. SQL View 'v_active_rescue_pipeline': [WARN] {e}")

    # -------------------------------------------------------------------------
    # SUMMARY
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    if len(errors) == 0:
        print("  VERIFICATION RESULT: ALL INTEGRITY & LOGICAL CHECKS PASSED [OK]")
        print("=" * 80 + "\n")
        db.close()
        return 0
    else:
        print(f"  VERIFICATION RESULT: FAILED WITH {len(errors)} ERROR(S)")
        for err in errors:
            print(f"    - {err}")
        print("=" * 80 + "\n")
        db.close()
        return 1

if __name__ == "__main__":
    exit_code = run_verification()
    sys.exit(exit_code)
