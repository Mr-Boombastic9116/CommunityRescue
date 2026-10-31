from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.pickup_request import PickupRequest
from app.models.food_batch import FoodBatch
from app.models.volunteer import Volunteer
from app.models.delivery_log import DeliveryLog
from app.models.notification import Notification
from app.models.donor import Donor
from app.models.ngo import NGOPartner
from app.services.allocation_service import AllocationService
from app.utils.dates import utc_now, to_naive_utc

class WorkflowService:
    @staticmethod
    def claim_pickup_task(db: Session, request_id: int, volunteer: Volunteer) -> PickupRequest:
        """
        Atomically claims a pickup request using MySQL row locking (with_for_update).
        Guarantees that two volunteers cannot claim the same task simultaneously.
        """
        # Step 1: Lock the pickup request row for update
        request = (
            db.query(PickupRequest)
            .filter(PickupRequest.request_id == request_id)
            .with_for_update()
            .first()
        )

        if not request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pickup task not found.",
            )

        # Concurrency verification: Is the task already assigned?
        if request.volunteer_id is not None or request.request_status != "requested":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This task has already been claimed by another volunteer or is no longer available.",
            )

        # Step 2: Lock and verify the food batch
        batch = (
            db.query(FoodBatch)
            .filter(FoodBatch.batch_id == request.batch_id)
            .with_for_update()
            .first()
        )

        if not batch:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Associated food batch not found.",
            )

        now = utc_now()
        exp = to_naive_utc(batch.expiry_time)

        # Verify expiry
        if exp <= now or batch.food_status == "expired":
            batch.food_status = "expired"
            request.request_status = "cancelled"
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot claim this task: the food donation has already expired.",
            )

        if batch.food_status in ["cancelled", "delivered", "collected"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot claim task: donation is currently '{batch.food_status}'.",
            )

        # Check volunteer availability
        if volunteer.availability_status == "offline":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot claim tasks while your status is set to Offline.",
            )

        # Step 3: Perform atomic updates
        request.volunteer_id = volunteer.volunteer_id
        request.request_status = "assigned"
        request.assigned_at = now
        AllocationService.update_batch_derived_status(db, batch)

        # Step 4: Record Delivery Log
        log = DeliveryLog(
            request_id=request.request_id,
            performed_by_user_id=volunteer.user_id,
            action="PICKUP_ASSIGNED",
            notes=f"Pickup task claimed by volunteer {volunteer.volunteer_name} (Phone: {volunteer.phone}).",
            logged_at=now,
        )
        db.add(log)

        # Step 5: Send in-app notifications
        # Notify NGO
        ngo = db.query(NGOPartner).filter(NGOPartner.ngo_id == request.ngo_id).first()
        if ngo:
            db.add(
                Notification(
                    user_id=ngo.user_id,
                    title="Volunteer Assigned",
                    message=f"Volunteer {volunteer.volunteer_name} has claimed pickup for '{batch.food_name}'.",
                )
            )

        # Notify Donor
        donor = db.query(Donor).filter(Donor.donor_id == batch.donor_id).first()
        if donor:
            db.add(
                Notification(
                    user_id=donor.user_id,
                    title="Pickup Scheduled",
                    message=f"Volunteer {volunteer.volunteer_name} is arriving to pick up '{batch.food_name}'.",
                )
            )

        try:
            db.commit()
            db.refresh(request)
            return request
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Transaction failed while claiming task: {str(e)}",
            )

    @staticmethod
    def mark_food_collected(db: Session, request_id: int, volunteer: Volunteer, notes: str = None) -> PickupRequest:
        request = (
            db.query(PickupRequest)
            .filter(PickupRequest.request_id == request_id)
            .with_for_update()
            .first()
        )

        if not request:
            raise HTTPException(status_code=404, detail="Pickup request not found.")

        if request.volunteer_id != volunteer.volunteer_id:
            raise HTTPException(status_code=403, detail="You are not authorized to update this task.")

        if request.request_status != "assigned":
            raise HTTPException(
                status_code=400,
                detail=f"Cannot mark as collected. Current task status is '{request.request_status}'.",
            )

        batch = db.query(FoodBatch).filter(FoodBatch.batch_id == request.batch_id).with_for_update().first()
        now = utc_now()

        request.request_status = "collected"
        request.collected_at = now
        if batch:
            AllocationService.update_batch_derived_status(db, batch)

        log = DeliveryLog(
            request_id=request.request_id,
            performed_by_user_id=volunteer.user_id,
            action="FOOD_COLLECTED",
            notes=notes or f"Food '{batch.food_name}' collected from pickup address by {volunteer.volunteer_name}.",
            logged_at=now,
        )
        db.add(log)

        # Notify NGO
        ngo = db.query(NGOPartner).filter(NGOPartner.ngo_id == request.ngo_id).first()
        if ngo:
            db.add(
                Notification(
                    user_id=ngo.user_id,
                    title="Food Collected",
                    message=f"Volunteer {volunteer.volunteer_name} has picked up '{batch.food_name}' and is in transit.",
                )
            )

        # Notify Donor
        donor = db.query(Donor).filter(Donor.donor_id == batch.donor_id).first()
        if donor:
            db.add(
                Notification(
                    user_id=donor.user_id,
                    title="Donation Collected",
                    message=f"Your donation '{batch.food_name}' was collected successfully.",
                )
            )

        try:
            db.commit()
            db.refresh(request)
            return request
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to record collection: {str(e)}")

    @staticmethod
    def mark_delivery_completed(db: Session, request_id: int, volunteer: Volunteer, notes: str = None) -> PickupRequest:
        request = (
            db.query(PickupRequest)
            .filter(PickupRequest.request_id == request_id)
            .with_for_update()
            .first()
        )

        if not request:
            raise HTTPException(status_code=404, detail="Pickup request not found.")

        if request.volunteer_id != volunteer.volunteer_id:
            raise HTTPException(status_code=403, detail="You are not authorized to update this task.")

        if request.request_status != "collected":
            raise HTTPException(
                status_code=400,
                detail=f"Cannot complete delivery. Current task status is '{request.request_status}'.",
            )

        batch = db.query(FoodBatch).filter(FoodBatch.batch_id == request.batch_id).with_for_update().first()
        now = utc_now()

        request.request_status = "delivered"
        request.completed_at = now
        if batch:
            AllocationService.update_batch_derived_status(db, batch)

        log = DeliveryLog(
            request_id=request.request_id,
            performed_by_user_id=volunteer.user_id,
            action="DELIVERY_COMPLETED",
            notes=notes or f"Food '{batch.food_name}' successfully delivered to NGO by {volunteer.volunteer_name}.",
            logged_at=now,
        )
        db.add(log)

        # Notify NGO
        ngo = db.query(NGOPartner).filter(NGOPartner.ngo_id == request.ngo_id).first()
        if ngo:
            db.add(
                Notification(
                    user_id=ngo.user_id,
                    title="Delivery Received",
                    message=f"Donation '{batch.food_name}' has been delivered to your location. Enjoy the meal!",
                )
            )

        # Notify Donor
        donor = db.query(Donor).filter(Donor.donor_id == batch.donor_id).first()
        if donor:
            db.add(
                Notification(
                    user_id=donor.user_id,
                    title="Donation Completed",
                    message=f"Thank you! Your donation '{batch.food_name}' was successfully delivered to {ngo.ngo_name if ngo else 'the NGO'}.",
                )
            )

        try:
            db.commit()
            db.refresh(request)
            return request
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to record delivery: {str(e)}")
