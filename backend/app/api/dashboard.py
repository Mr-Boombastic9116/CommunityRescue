from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.session import get_db
from app.models.user import User
from app.models.donor import Donor
from app.models.ngo import NGOPartner
from app.models.volunteer import Volunteer
from app.models.food_batch import FoodBatch
from app.models.pickup_request import PickupRequest
from app.models.delivery_log import DeliveryLog
from app.api.deps import get_current_user
from app.services.expiry_service import process_food_expiries

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/public-summary")
def get_public_impact_summary(db: Session = Depends(get_db)):
    process_food_expiries(db)

    # Total quantity delivered
    total_qty = (
        db.query(func.coalesce(func.sum(PickupRequest.requested_quantity), 0.0))
        .filter(PickupRequest.request_status == "delivered")
        .scalar()
    )
    if not total_qty or float(total_qty) == 0.0:
        total_qty = (
            db.query(func.coalesce(func.sum(FoodBatch.quantity), 0.0))
            .filter(FoodBatch.food_status == "delivered")
            .scalar()
        )

    # Total completed deliveries
    completed_deliveries = (
        db.query(func.count(PickupRequest.request_id))
        .filter(PickupRequest.request_status == "delivered")
        .scalar()
    )

    # Active available batches right now (available or partially_reserved)
    active_donations = (
        db.query(func.count(FoodBatch.batch_id))
        .filter(FoodBatch.food_status.in_(["available", "partially_reserved"]))
        .scalar()
    )

    # Community counts
    donors_count = db.query(func.count(Donor.donor_id)).scalar()
    ngos_count = db.query(func.count(NGOPartner.ngo_id)).scalar()
    volunteers_count = db.query(func.count(Volunteer.volunteer_id)).scalar()

    return {
        "total_food_rescued_kg": float(total_qty or 0.0),
        "completed_deliveries": completed_deliveries or 0,
        "active_available_donations": active_donations or 0,
        "total_donors": donors_count or 0,
        "total_ngos": ngos_count or 0,
        "total_volunteers": volunteers_count or 0,
    }

@router.get("/stats")
def get_role_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    process_food_expiries(db)

    if current_user.role == "donor" and current_user.donor:
        donor_id = current_user.donor.donor_id

        total = db.query(func.count(FoodBatch.batch_id)).filter(FoodBatch.donor_id == donor_id).scalar() or 0
        available = db.query(func.count(FoodBatch.batch_id)).filter(
            FoodBatch.donor_id == donor_id,
            FoodBatch.food_status.in_(["available", "partially_reserved"]),
        ).scalar() or 0
        in_progress = db.query(func.count(FoodBatch.batch_id)).filter(
            FoodBatch.donor_id == donor_id,
            FoodBatch.food_status.in_(["requested", "assigned", "collected", "reserved"]),
        ).scalar() or 0
        completed = db.query(func.count(FoodBatch.batch_id)).filter(FoodBatch.donor_id == donor_id, FoodBatch.food_status == "delivered").scalar() or 0
        expired = db.query(func.count(FoodBatch.batch_id)).filter(FoodBatch.donor_id == donor_id, FoodBatch.food_status == "expired").scalar() or 0

        total_qty = (
            db.query(func.coalesce(func.sum(PickupRequest.requested_quantity), 0.0))
            .join(FoodBatch, PickupRequest.batch_id == FoodBatch.batch_id)
            .filter(FoodBatch.donor_id == donor_id, PickupRequest.request_status == "delivered")
            .scalar()
        )
        if not total_qty or float(total_qty) == 0.0:
            total_qty = db.query(func.coalesce(func.sum(FoodBatch.quantity), 0.0)).filter(
                FoodBatch.donor_id == donor_id,
                FoodBatch.food_status == "delivered"
            ).scalar() or 0.0

        # Recent batches
        recent_batches = (
            db.query(FoodBatch)
            .filter(FoodBatch.donor_id == donor_id)
            .order_by(FoodBatch.created_at.desc())
            .limit(5)
            .all()
        )

        activities = [
            {
                "id": b.batch_id,
                "title": b.food_name,
                "status": b.food_status,
                "time": b.created_at.isoformat(),
                "details": f"{b.quantity} {b.unit} ({b.food_category})",
            }
            for b in recent_batches
        ]

        return {
            "role": "donor",
            "total_donations": total,
            "available_donations": available,
            "in_progress_donations": in_progress,
            "completed_donations": completed,
            "expired_donations": expired,
            "total_quantity_donated": float(total_qty),
            "recent_activities": activities,
        }

    elif current_user.role == "ngo" and current_user.ngo:
        ngo_id = current_user.ngo.ngo_id

        total_reqs = db.query(func.count(PickupRequest.request_id)).filter(PickupRequest.ngo_id == ngo_id).scalar() or 0
        pending = db.query(func.count(PickupRequest.request_id)).filter(PickupRequest.ngo_id == ngo_id, PickupRequest.request_status == "requested").scalar() or 0
        assigned = db.query(func.count(PickupRequest.request_id)).filter(PickupRequest.ngo_id == ngo_id, PickupRequest.request_status == "assigned").scalar() or 0
        collected = db.query(func.count(PickupRequest.request_id)).filter(PickupRequest.ngo_id == ngo_id, PickupRequest.request_status == "collected").scalar() or 0
        completed = db.query(func.count(PickupRequest.request_id)).filter(PickupRequest.ngo_id == ngo_id, PickupRequest.request_status == "delivered").scalar() or 0
        cancelled = db.query(func.count(PickupRequest.request_id)).filter(PickupRequest.ngo_id == ngo_id, PickupRequest.request_status == "cancelled").scalar() or 0

        # Total quantity received
        total_received_qty = (
            db.query(func.coalesce(func.sum(PickupRequest.requested_quantity), 0.0))
            .filter(PickupRequest.ngo_id == ngo_id, PickupRequest.request_status == "delivered")
            .scalar() or 0.0
        )
        if not total_received_qty or float(total_received_qty) == 0.0:
            total_received_qty = (
                db.query(func.coalesce(func.sum(FoodBatch.quantity), 0.0))
                .join(PickupRequest, FoodBatch.batch_id == PickupRequest.batch_id)
                .filter(PickupRequest.ngo_id == ngo_id, PickupRequest.request_status == "delivered")
                .scalar() or 0.0
            )

        recent_reqs = (
            db.query(PickupRequest)
            .filter(PickupRequest.ngo_id == ngo_id)
            .order_by(PickupRequest.requested_at.desc())
            .limit(5)
            .all()
        )

        activities = [
            {
                "id": r.request_id,
                "title": r.food_batch.food_name if r.food_batch else "Donation",
                "status": r.request_status,
                "time": r.requested_at.isoformat(),
                "details": f"Status: {r.request_status.capitalize()}",
            }
            for r in recent_reqs
        ]

        return {
            "role": "ngo",
            "total_requests": total_reqs,
            "pending_requests": pending,
            "assigned_requests": assigned,
            "collected_requests": collected,
            "completed_requests": completed,
            "cancelled_requests": cancelled,
            "total_quantity_received": float(total_received_qty),
            "recent_activities": activities,
        }

    elif current_user.role == "volunteer" and current_user.volunteer:
        volunteer_id = current_user.volunteer.volunteer_id

        total_claimed = db.query(func.count(PickupRequest.request_id)).filter(PickupRequest.volunteer_id == volunteer_id).scalar() or 0
        assigned = db.query(func.count(PickupRequest.request_id)).filter(PickupRequest.volunteer_id == volunteer_id, PickupRequest.request_status == "assigned").scalar() or 0
        collected = db.query(func.count(PickupRequest.request_id)).filter(PickupRequest.volunteer_id == volunteer_id, PickupRequest.request_status == "collected").scalar() or 0
        completed = db.query(func.count(PickupRequest.request_id)).filter(PickupRequest.volunteer_id == volunteer_id, PickupRequest.request_status == "delivered").scalar() or 0

        recent_tasks = (
            db.query(PickupRequest)
            .filter(PickupRequest.volunteer_id == volunteer_id)
            .order_by(PickupRequest.updated_at.desc())
            .limit(5)
            .all()
        )

        activities = [
            {
                "id": t.request_id,
                "title": t.food_batch.food_name if t.food_batch else "Task",
                "status": t.request_status,
                "time": t.updated_at.isoformat(),
                "details": f"Status: {t.request_status.capitalize()}",
            }
            for t in recent_tasks
        ]

        return {
            "role": "volunteer",
            "total_claimed": total_claimed,
            "assigned_tasks": assigned,
            "collected_tasks": collected,
            "completed_tasks": completed,
            "availability_status": current_user.volunteer.availability_status,
            "recent_activities": activities,
        }

    return {}

