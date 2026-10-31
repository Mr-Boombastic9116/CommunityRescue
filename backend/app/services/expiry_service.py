import asyncio
from datetime import datetime
from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.models.food_batch import FoodBatch
from app.models.pickup_request import PickupRequest
from app.models.delivery_log import DeliveryLog
from app.models.notification import Notification
from app.utils.dates import utc_now, to_naive_utc

def calculate_expiry_metadata(batch: FoodBatch):
    """
    Calculates remaining holding hours, close-to-expiry flag, and 4-tier urgency level:
    - Green ('safe'): plenty of time remaining (> 4.0 hours)
    - Orange ('approaching'): approaching expiry (2.0 < hours <= 4.0)
    - Red ('urgent'): urgent redistribution needed (0 < hours <= 2.0)
    - Grey ('expired'): passed expiry or marked expired (hours <= 0.0)
    """
    now = utc_now()
    exp = to_naive_utc(batch.expiry_time)
    diff = (exp - now).total_seconds()
    remaining_hours = max(0.0, round(diff / 3600.0, 1))

    if diff <= 0 or batch.food_status == "expired":
        urgency_level = "expired"
        is_close = False
    elif remaining_hours <= 2.0:
        urgency_level = "urgent"
        is_close = True
    elif remaining_hours <= 4.0:
        urgency_level = "approaching"
        is_close = True
    else:
        urgency_level = "safe"
        is_close = False

    return remaining_hours, is_close, urgency_level

def process_food_expiries(db: Session) -> int:
    """
    Checks all batches and marks expired food appropriately.
    Idempotent: Only updates active batches that have passed expiry_time.
    Does NOT expire food that has already been collected or delivered.
    """
    now = utc_now()
    
    # Query active batches that have passed their effective expiry time
    expired_batches = (
        db.query(FoodBatch)
        .filter(
            FoodBatch.expiry_time <= now,
            FoodBatch.food_status.in_(["available", "partially_reserved", "requested"])
        )
        .all()
    )

    count = 0
    for batch in expired_batches:
        batch.food_status = "expired"
        count += 1

        # Cancel any active uncollected requests for this batch
        active_requests = (
            db.query(PickupRequest)
            .filter(
                PickupRequest.batch_id == batch.batch_id,
                PickupRequest.request_status.in_(["requested", "assigned"])
            )
            .all()
        )

        for req in active_requests:
            req.request_status = "cancelled"
            log = DeliveryLog(
                request_id=req.request_id,
                action="DONATION_EXPIRED",
                notes=f"Food '{batch.food_name}' expired before courier collection.",
                logged_at=now,
            )
            db.add(log)

            # Notify NGO
            if req.ngo:
                db.add(
                    Notification(
                        user_id=req.ngo.user_id,
                        title="Donation Expired",
                        message=f"Requested food '{batch.food_name}' has passed its expiry threshold and the request was automatically cancelled.",
                    )
                )

        # Notify donor
        if batch.donor:
            db.add(
                Notification(
                    user_id=batch.donor.user_id,
                    title="Donation Expired",
                    message=f"Your food batch '{batch.food_name}' has passed its maximum safe holding expiry and is now marked Expired.",
                )
            )

    if count > 0:
        try:
            db.commit()
            print(f"[ExpiryService] Successfully marked {count} batches as expired.")
        except Exception as e:
            db.rollback()
            print(f"[ExpiryService] Error committing expiry updates: {e}")

    return count

async def expiry_background_task(interval_seconds: int = 60):
    """
    Runs in the background of FastAPI and periodically checks for expired batches.
    """
    while True:
        try:
            db = SessionLocal()
            try:
                process_food_expiries(db)
            finally:
                db.close()
        except Exception as e:
            print(f"[ExpiryBackgroundTask] Error in periodic check: {e}")
        await asyncio.sleep(interval_seconds)
