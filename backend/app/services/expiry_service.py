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
    now = utc_now()
    exp = to_naive_utc(batch.expiry_time)
    diff = (exp - now).total_seconds()
    remaining_hours = max(0.0, round(diff / 3600.0, 1))
    # Close to expiry if remaining time is between 0 and 4 hours and status is active
    is_close = 0 < remaining_hours <= 4.0 and batch.food_status in ["available", "requested", "assigned"]
    return remaining_hours, is_close

def process_food_expiries(db: Session) -> int:
    """
    Checks all batches and marks expired food appropriately.
    Does NOT expire food that has already been collected or delivered.
    """
    now = utc_now()
    
    # Query batches that have passed expiry time and are still in available or requested status
    expired_batches = (
        db.query(FoodBatch)
        .filter(
            FoodBatch.expiry_time <= now,
            FoodBatch.food_status.in_(["available", "requested"])
        )
        .all()
    )

    count = 0
    for batch in expired_batches:
        prev_status = batch.food_status
        batch.food_status = "expired"
        count += 1

        # If it had an active request that was not yet picked up
        active_request = (
            db.query(PickupRequest)
            .filter(
                PickupRequest.batch_id == batch.batch_id,
                PickupRequest.request_status == "requested"
            )
            .first()
        )

        if active_request:
            active_request.request_status = "cancelled"
            log = DeliveryLog(
                request_id=active_request.request_id,
                action="DONATION_EXPIRED",
                notes=f"Food '{batch.food_name}' expired before volunteer assignment.",
                logged_at=now,
            )
            db.add(log)

            # Notify NGO
            if active_request.ngo:
                db.add(
                    Notification(
                        user_id=active_request.ngo.user_id,
                        title="Donation Expired",
                        message=f"Requested food '{batch.food_name}' has expired and request was automatically cancelled.",
                    )
                )

        # Notify donor
        if batch.donor:
            db.add(
                Notification(
                    user_id=batch.donor.user_id,
                    title="Donation Expired",
                    message=f"Your food batch '{batch.food_name}' has passed its expiry time and is now marked Expired.",
                )
            )

    if count > 0:
        try:
            db.commit()
            print(f"[ExpiryService] Successfully updated {count} expired food batches.")
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
            print(f"[ExpiryService Background Error]: {e}")
        await asyncio.sleep(interval_seconds)
