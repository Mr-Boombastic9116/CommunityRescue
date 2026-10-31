from decimal import Decimal
from typing import Tuple, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status
from app.models.food_batch import FoodBatch
from app.models.pickup_request import PickupRequest
from app.utils.dates import utc_now, to_naive_utc

# Request statuses that hold an active allocation or have completed delivery
ALLOCATED_REQUEST_STATUSES = ["requested", "assigned", "collected", "delivered"]

class AllocationService:
    @staticmethod
    def calculate_remaining_quantity(db: Session, batch_id: int) -> Tuple[Decimal, Decimal, Decimal]:
        """
        Calculates (donated_quantity, allocated_quantity, remaining_quantity)
        for a given batch.
        """
        batch = db.query(FoodBatch).filter(FoodBatch.batch_id == batch_id).first()
        if not batch:
            return Decimal("0.0"), Decimal("0.0"), Decimal("0.0")

        total_qty = Decimal(str(batch.quantity))

        # Sum requested_quantity for active requests
        allocated_sum = (
            db.query(func.coalesce(func.sum(PickupRequest.requested_quantity), 0.0))
            .filter(
                PickupRequest.batch_id == batch_id,
                PickupRequest.request_status.in_(ALLOCATED_REQUEST_STATUSES),
            )
            .scalar()
        )
        allocated_qty = Decimal(str(allocated_sum or 0.0))
        remaining_qty = max(Decimal("0.0"), total_qty - allocated_qty)
        return total_qty, allocated_qty, remaining_qty

    @staticmethod
    def update_batch_derived_status(db: Session, batch: FoodBatch) -> str:
        """
        Recalculates remaining quantity and updates the batch's food_status appropriately.
        Preserves terminal states ('expired', 'cancelled').
        """
        now = utc_now()
        exp = to_naive_utc(batch.expiry_time)
        if exp <= now or batch.food_status == "expired":
            batch.food_status = "expired"
            return "expired"

        if batch.food_status == "cancelled":
            return "cancelled"

        total_qty = Decimal(str(batch.quantity))
        
        # Get all requests for this batch
        requests = db.query(PickupRequest).filter(PickupRequest.batch_id == batch.batch_id).all()
        active_requests = [r for r in requests if r.request_status in ALLOCATED_REQUEST_STATUSES]

        if not active_requests:
            batch.food_status = "available"
            return "available"

        allocated_qty = sum(Decimal(str(r.requested_quantity)) for r in active_requests)
        remaining_qty = max(Decimal("0.0"), total_qty - allocated_qty)

        # Check if all active requests are delivered
        if active_requests and all(r.request_status == "delivered" for r in active_requests) and remaining_qty == 0:
            batch.food_status = "delivered"
            return "delivered"

        # Check if fully reserved vs partially reserved
        if remaining_qty <= Decimal("0.0"):
            # Check if all active requests are collected or delivered
            if all(r.request_status in ["collected", "delivered"] for r in active_requests):
                batch.food_status = "collected"
            elif any(r.request_status in ["assigned", "collected"] for r in active_requests):
                batch.food_status = "assigned"
            else:
                batch.food_status = "reserved"
            return batch.food_status

        if 0 < remaining_qty < total_qty:
            batch.food_status = "partially_reserved"
            return "partially_reserved"

        batch.food_status = "available"
        return "available"

    @staticmethod
    def allocate_quantity_atomic(
        db: Session,
        batch_id: int,
        requested_quantity: Decimal,
    ) -> FoodBatch:
        """
        Safely and atomically verifies remaining quantity with row locking (with_for_update)
        and adjusts batch status.
        """
        if requested_quantity <= Decimal("0.0"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Requested quantity must be strictly greater than 0.",
            )

        # Lock the batch row
        batch = db.query(FoodBatch).filter(FoodBatch.batch_id == batch_id).with_for_update().first()
        if not batch:
            raise HTTPException(status_code=404, detail="Food batch not found.")

        now = utc_now()
        exp = to_naive_utc(batch.expiry_time)
        if exp <= now or batch.food_status == "expired":
            batch.food_status = "expired"
            db.commit()
            raise HTTPException(status_code=400, detail="Cannot request food: this donation has expired.")

        if batch.food_status in ["cancelled", "delivered", "expired"]:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot request food: donation is currently '{batch.food_status}'.",
            )

        # Calculate current allocated quantity using row locks on active requests
        active_requests = (
            db.query(PickupRequest)
            .filter(
                PickupRequest.batch_id == batch_id,
                PickupRequest.request_status.in_(ALLOCATED_REQUEST_STATUSES),
            )
            .with_for_update()
            .all()
        )
        current_allocated = sum(Decimal(str(r.requested_quantity)) for r in active_requests)
        total_qty = Decimal(str(batch.quantity))
        remaining_qty = max(Decimal("0.0"), total_qty - current_allocated)

        if requested_quantity > remaining_qty:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Requested quantity ({requested_quantity} {batch.unit}) exceeds "
                    f"remaining available quantity ({remaining_qty} {batch.unit})."
                ),
            )

        # New remaining quantity after this allocation
        new_remaining = remaining_qty - requested_quantity
        if new_remaining <= Decimal("0.0"):
            batch.food_status = "reserved"
        else:
            batch.food_status = "partially_reserved"

        return batch

