from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.notification import Notification
from app.models.user import User
from app.utils.dates import utc_now

class NotificationService:
    @classmethod
    def create_notification(
        cls,
        db: Session,
        user_id: int,
        title: str,
        message: str,
        notification_type: Optional[str] = None,
        reference_id: Optional[int] = None,
        role_target: Optional[str] = None,
        avoid_duplicate_minutes: int = 10,
    ) -> Optional[Notification]:
        """
        Creates an in-app notification avoiding duplicates within a short time window.
        """
        now = utc_now()
        # Check for recent identical notification
        if avoid_duplicate_minutes > 0:
            from datetime import timedelta
            cutoff = now - timedelta(minutes=avoid_duplicate_minutes)
            existing = db.query(Notification).filter(
                Notification.user_id == user_id,
                Notification.title == title,
                Notification.created_at >= cutoff
            ).first()
            if existing:
                return existing

        notif = Notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            reference_id=reference_id,
            role_target=role_target,
            is_read=False,
            created_at=now,
        )
        db.add(notif)
        db.commit()
        db.refresh(notif)
        return notif

    # -------------------------------------------------------------------------
    # DONOR EVENT NOTIFICATIONS
    # -------------------------------------------------------------------------
    @classmethod
    def notify_donor_claim_submitted(cls, db: Session, donor_user_id: int, ngo_name: str, food_name: str, qty: float, unit: str, req_id: int):
        cls.create_notification(
            db,
            user_id=donor_user_id,
            title="New Portion Claim Received",
            message=f"{ngo_name} has requested {qty} {unit} of '{food_name}'.",
            notification_type="donor_claim_submitted",
            reference_id=req_id,
            role_target="donor",
        )

    @classmethod
    def notify_donor_volunteer_assigned(cls, db: Session, donor_user_id: int, volunteer_name: str, food_name: str, req_id: int, pickup_code: str):
        cls.create_notification(
            db,
            user_id=donor_user_id,
            title="Courier Dispatched for Pickup",
            message=f"Volunteer courier {volunteer_name} accepted delivery of '{food_name}'. Please share Pickup Code: {pickup_code} upon handover.",
            notification_type="donor_volunteer_assigned",
            reference_id=req_id,
            role_target="donor",
        )

    @classmethod
    def notify_donor_food_collected(cls, db: Session, donor_user_id: int, volunteer_name: str, food_name: str, req_id: int):
        cls.create_notification(
            db,
            user_id=donor_user_id,
            title="Food Collected by Courier",
            message=f"Courier {volunteer_name} verified pickup of '{food_name}'. Package is now en route to shelter.",
            notification_type="donor_food_collected",
            reference_id=req_id,
            role_target="donor",
        )

    @classmethod
    def notify_donor_food_delivered(cls, db: Session, donor_user_id: int, ngo_name: str, food_name: str, req_id: int):
        cls.create_notification(
            db,
            user_id=donor_user_id,
            title="Redistribution Completed!",
            message=f"Your donation of '{food_name}' was safely delivered to {ngo_name}. Thank you for rescuing surplus meals!",
            notification_type="donor_food_delivered",
            reference_id=req_id,
            role_target="donor",
        )

    # -------------------------------------------------------------------------
    # NGO EVENT NOTIFICATIONS
    # -------------------------------------------------------------------------
    @classmethod
    def notify_ngo_volunteer_assigned(cls, db: Session, ngo_user_id: int, volunteer_name: str, food_name: str, req_id: int):
        cls.create_notification(
            db,
            user_id=ngo_user_id,
            title="Volunteer Courier Assigned",
            message=f"Courier {volunteer_name} has claimed pickup for '{food_name}'. Delivery is being initiated.",
            notification_type="ngo_volunteer_assigned",
            reference_id=req_id,
            role_target="ngo",
        )

    @classmethod
    def notify_ngo_food_collected(cls, db: Session, ngo_user_id: int, volunteer_name: str, food_name: str, req_id: int, delivery_code: str):
        cls.create_notification(
            db,
            user_id=ngo_user_id,
            title="Food Collected — In Transit",
            message=f"Courier {volunteer_name} collected '{food_name}'. Share Delivery Code: {delivery_code} upon shelter arrival.",
            notification_type="ngo_food_collected",
            reference_id=req_id,
            role_target="ngo",
        )

    @classmethod
    def notify_ngo_delivery_completed(cls, db: Session, ngo_user_id: int, food_name: str, qty: float, unit: str, req_id: int):
        cls.create_notification(
            db,
            user_id=ngo_user_id,
            title="Delivery Verified & Received",
            message=f"Successfully received {qty} {unit} of '{food_name}'. Meals added to distribution log.",
            notification_type="ngo_delivery_completed",
            reference_id=req_id,
            role_target="ngo",
        )

    # -------------------------------------------------------------------------
    # VOLUNTEER EVENT NOTIFICATIONS
    # -------------------------------------------------------------------------
    @classmethod
    def notify_volunteer_task_claimed(cls, db: Session, vol_user_id: int, donor_name: str, address: str, req_id: int):
        cls.create_notification(
            db,
            user_id=vol_user_id,
            title="Pickup Assignment Locked",
            message=f"You are assigned to pickup from {donor_name} at {address}. Obtain the 6-digit pickup OTP at handover.",
            notification_type="vol_task_claimed",
            reference_id=req_id,
            role_target="volunteer",
        )

    @classmethod
    def notify_volunteers_new_urgent_task(cls, db: Session, volunteers: List[User], food_name: str, address: str, req_id: int):
        for vol in volunteers:
            cls.create_notification(
                db,
                user_id=vol.user_id,
                title="Urgent Pickup Task Available!",
                message=f"Immediate rescue needed for '{food_name}' at {address}. Claim now to prevent expiration.",
                notification_type="vol_urgent_task",
                reference_id=req_id,
                role_target="volunteer",
                avoid_duplicate_minutes=30,
            )

