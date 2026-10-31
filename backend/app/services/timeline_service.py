from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.food_batch import FoodBatch
from app.models.pickup_request import PickupRequest
from app.models.delivery_log import DeliveryLog
from app.models.user import User

class TimelineService:
    @classmethod
    def get_batch_timeline(cls, db: Session, batch_id: int, requesting_user: Optional[User] = None) -> List[Dict[str, Any]]:
        """
        Builds the chronological lifecycle timeline for a food donation batch.
        """
        batch = db.query(FoodBatch).filter(FoodBatch.batch_id == batch_id).first()
        if not batch:
            return []

        events: List[Dict[str, Any]] = []

        # 1. Donation Created Event
        events.append({
            "stage_number": 1,
            "event_type": "donation_created",
            "title": "Donation Listed",
            "description": f"Batch '{batch.food_name}' ({batch.quantity} {batch.unit}) listed by {batch.donor.donor_name if batch.donor else 'Donor'}.",
            "timestamp": batch.created_at.isoformat(),
            "status": "completed",
            "actor_name": batch.donor.donor_name if batch.donor else "Donor",
            "actor_role": "donor",
        })

        # 2. Iterate through requests and delivery logs
        requests = db.query(PickupRequest).filter(PickupRequest.batch_id == batch_id).all()
        for req in requests:
            # Request Submitted
            events.append({
                "stage_number": 2,
                "event_type": "request_submitted",
                "title": f"NGO Claim #{req.request_id} Submitted",
                "description": f"{req.ngo.ngo_name if req.ngo else 'NGO'} claimed {req.requested_quantity} {req.unit}.",
                "timestamp": req.requested_at.isoformat(),
                "status": "completed",
                "actor_name": req.ngo.ngo_name if req.ngo else "NGO Partner",
                "actor_role": "ngo",
                "request_id": req.request_id,
            })

            # Volunteer Assigned
            if req.assigned_at and req.volunteer:
                events.append({
                    "stage_number": 3,
                    "event_type": "volunteer_assigned",
                    "title": f"Courier Assigned to Claim #{req.request_id}",
                    "description": f"Volunteer {req.volunteer.volunteer_name} locked delivery assignment.",
                    "timestamp": req.assigned_at.isoformat(),
                    "status": "completed",
                    "actor_name": req.volunteer.volunteer_name,
                    "actor_role": "volunteer",
                    "request_id": req.request_id,
                })

            # Pickup Verified & Collected
            if req.collected_at:
                events.append({
                    "stage_number": 4,
                    "event_type": "food_collected",
                    "title": f"Food Collected for Claim #{req.request_id}",
                    "description": f"Pickup verification completed with OTP. Food collected from donor.",
                    "timestamp": req.collected_at.isoformat(),
                    "status": "completed",
                    "actor_name": req.volunteer.volunteer_name if req.volunteer else "Volunteer",
                    "actor_role": "volunteer",
                    "request_id": req.request_id,
                })

            # Completed / Delivered
            if req.completed_at and req.request_status == "delivered":
                events.append({
                    "stage_number": 5,
                    "event_type": "food_delivered",
                    "title": f"Claim #{req.request_id} Safely Delivered",
                    "description": f"Delivery verification code verified at {req.ngo.ngo_name if req.ngo else 'NGO'} shelter.",
                    "timestamp": req.completed_at.isoformat(),
                    "status": "completed",
                    "actor_name": req.volunteer.volunteer_name if req.volunteer else "Volunteer",
                    "actor_role": "volunteer",
                    "request_id": req.request_id,
                })
            elif req.request_status in ["cancelled", "rejected"]:
                events.append({
                    "stage_number": 5,
                    "event_type": f"request_{req.request_status}",
                    "title": f"Claim #{req.request_id} {req.request_status.capitalize()}",
                    "description": f"Portion reservation released back to available surplus.",
                    "timestamp": req.updated_at.isoformat(),
                    "status": "cancelled",
                    "actor_name": "System",
                    "actor_role": "system",
                    "request_id": req.request_id,
                })

        # Append custom log entries from delivery_logs
        logs = db.query(DeliveryLog).filter(
            (DeliveryLog.batch_id == batch_id) |
            (DeliveryLog.request_id.in_([r.request_id for r in requests]))
        ).all()

        for l in logs:
            if l.action not in ["pickup_verified_collected", "delivery_verified_completed"]:
                events.append({
                    "stage_number": 6,
                    "event_type": l.action,
                    "title": l.action.replace("_", " ").title(),
                    "description": l.notes or "",
                    "timestamp": l.logged_at.isoformat(),
                    "status": "completed",
                    "actor_name": l.performed_by_user.name if l.performed_by_user else "System",
                    "actor_role": l.performed_by_user.role if l.performed_by_user else "system",
                })

        events.sort(key=lambda x: x["timestamp"])
        return events

    @classmethod
    def get_request_timeline(cls, db: Session, request_id: int, requesting_user: Optional[User] = None) -> List[Dict[str, Any]]:
        """
        Builds the 9-stage lifecycle timeline for an individual pickup request:
        1. Created / Listed
        2. Verified (FSSAI)
        3. Matched & Recommended
        4. Requested / Claimed
        5. Courier Assigned
        6. Picked Up (Handover OTP Verified)
        7. In Transit
        8. Delivered (Shelter OTP Verified)
        9. Completed & Impact Logged
        """
        req = db.query(PickupRequest).filter(PickupRequest.request_id == request_id).first()
        if not req:
            return []

        batch = req.food_batch
        donor_name = batch.donor.donor_name if batch and batch.donor else "Donor"
        ngo_name = req.ngo.ngo_name if req.ngo else "NGO"
        vol_name = req.volunteer.volunteer_name if req.volunteer else "Courier"

        is_assigned = req.assigned_at is not None
        is_collected = req.collected_at is not None
        is_delivered = req.completed_at is not None or req.request_status == "delivered"
        is_cancelled = req.request_status in ["cancelled", "rejected"]

        stages = [
            # Stage 1: Created / Listed
            {
                "stage_number": 1,
                "key": "created",
                "title": "Donation Listed",
                "description": f"Surplus '{batch.food_name if batch else 'Food'}' ({req.requested_quantity} {req.unit}) listed by {donor_name}.",
                "timestamp": batch.created_at.isoformat() if batch else None,
                "status": "completed",
                "actor": donor_name,
                "role": "donor",
            },
            # Stage 2: Verified (FSSAI Expiry Verified)
            {
                "stage_number": 2,
                "key": "fssai_verified",
                "title": "FSSAI Safety Verified",
                "description": f"Validated against food safety guidelines ({batch.expiry_rule_applied or 'Standard Safety Threshold'}). Effective expiry locked.",
                "timestamp": batch.created_at.isoformat() if batch else None,
                "status": "completed",
                "actor": "FSSAI Compliance Engine",
                "role": "system",
            },
            # Stage 3: Matched & Recommended
            {
                "stage_number": 3,
                "key": "matched",
                "title": "Smart NGO Match Discovered",
                "description": f"Multi-factor matching ranked {ngo_name} based on distance, category fit, and capacity.",
                "timestamp": req.requested_at.isoformat(),
                "status": "completed",
                "actor": "Smart Matching Engine",
                "role": "system",
            },
            # Stage 4: Requested / Claimed
            {
                "stage_number": 4,
                "key": "requested",
                "title": "Portion Reserved by NGO",
                "description": f"{ngo_name} submitted portion reservation for {req.requested_quantity} {req.unit}.",
                "timestamp": req.requested_at.isoformat(),
                "status": "completed",
                "actor": ngo_name,
                "role": "ngo",
            },
            # Stage 5: Courier Assigned
            {
                "stage_number": 5,
                "key": "assigned",
                "title": "Courier Assigned",
                "description": f"Volunteer {vol_name} locked pickup task. Stage 1 Handover OTP generated." if is_assigned else "Awaiting volunteer courier to accept assignment.",
                "timestamp": req.assigned_at.isoformat() if is_assigned else None,
                "status": "completed" if is_assigned else ("cancelled" if is_cancelled else "current"),
                "actor": vol_name if is_assigned else "Volunteer Network",
                "role": "volunteer",
            },
            # Stage 6: Picked Up / Handover Verified
            {
                "stage_number": 6,
                "key": "collected",
                "title": "Pickup Handover Verified",
                "description": "Secure 6-digit OTP verified at donor location. Food handed to courier." if is_collected else "Courier arrives at donor address and inputs donor OTP.",
                "timestamp": req.collected_at.isoformat() if is_collected else None,
                "status": "completed" if is_collected else ("cancelled" if is_cancelled else ("current" if is_assigned else "pending")),
                "actor": f"{donor_name} & {vol_name}",
                "role": "verification",
            },
            # Stage 7: In Transit
            {
                "stage_number": 7,
                "key": "in_transit",
                "title": "Food In Transit",
                "description": "Courier is transporting surplus to destination shelter." if is_collected and not is_delivered else ("Transport completed." if is_delivered else "Awaiting pickup collection."),
                "timestamp": req.collected_at.isoformat() if is_collected else None,
                "status": "completed" if is_delivered else ("current" if is_collected else "pending"),
                "actor": vol_name,
                "role": "volunteer",
            },
            # Stage 8: Delivered & Handover Verified
            {
                "stage_number": 8,
                "key": "delivered",
                "title": "Delivery Handover Verified",
                "description": f"Stage 2 Delivery OTP verified with {ngo_name} shelter staff. Food accepted." if is_delivered else f"Courier arrives at {ngo_name} and inputs shelter OTP.",
                "timestamp": req.completed_at.isoformat() if is_delivered else None,
                "status": "completed" if is_delivered else ("cancelled" if is_cancelled else ("current" if is_collected else "pending")),
                "actor": f"{ngo_name} & {vol_name}",
                "role": "verification",
            },
            # Stage 9: Completed & Closed
            {
                "stage_number": 9,
                "key": "completed",
                "title": "Redistribution Completed",
                "description": "Surplus rescue finalized. Meals served to community beneficiaries." if is_delivered else "Awaiting delivery confirmation.",
                "timestamp": req.completed_at.isoformat() if is_delivered else None,
                "status": "completed" if is_delivered else ("cancelled" if is_cancelled else "pending"),
                "actor": "Community Food Rescue Network",
                "role": "system",
            },
        ]

        if is_cancelled:
            stages.append({
                "stage_number": 10,
                "key": "cancelled",
                "title": f"Request {req.request_status.capitalize()}",
                "description": f"Request cancelled; reserved quantity released back to surplus.",
                "timestamp": req.updated_at.isoformat(),
                "status": "cancelled",
                "actor": "System",
                "role": "system",
            })

        return stages
