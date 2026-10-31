import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.pickup_request import PickupRequest
from app.models.delivery_log import DeliveryLog
from app.utils.dates import utc_now, to_naive_utc

SALT = "CFRN_HANDOVER_SECURE_SALT_v1"

class VerificationService:
    @staticmethod
    def hash_code(code: str) -> str:
        """Cryptographically hashes a 6-digit OTP code using SHA-256 with salt."""
        cleaned = str(code).strip()
        return hashlib.sha256(f"{SALT}:{cleaned}".encode("utf-8")).hexdigest()

    @staticmethod
    def generate_otp() -> Tuple[str, str, str]:
        """
        Generates a secure 6-digit OTP code, its hash, and a unique QR token.
        Returns: (plain_code, hashed_code, qr_token)
        """
        # Cryptographically secure 6-digit code between 100000 and 999999
        plain_code = f"{secrets.randbelow(900000) + 100000}"
        hashed = VerificationService.hash_code(plain_code)
        qr_token = secrets.token_urlsafe(32)
        return plain_code, hashed, qr_token

    @classmethod
    def setup_pickup_verification(cls, db: Session, request: PickupRequest) -> str:
        """
        Generates and saves the Stage 1 pickup OTP hash on the pickup request.
        Returns the plaintext OTP (to be communicated to the donor or displayed in donor portal).
        """
        plain_otp, hashed_otp, qr_token = cls.generate_otp()
        request.pickup_otp_hash = hashed_otp
        request.qr_token = qr_token
        request.pickup_attempts_count = 0
        # Expires in 24 hours or food expiry, whichever is earlier
        max_valid = utc_now() + timedelta(hours=24)
        if request.food_batch and request.food_batch.expiry_time:
            expiry = to_naive_utc(request.food_batch.expiry_time)
            request.pickup_otp_expires_at = min(max_valid, expiry)
        else:
            request.pickup_otp_expires_at = max_valid

        db.commit()
        db.refresh(request)
        return plain_otp

    @classmethod
    def setup_delivery_verification(cls, db: Session, request: PickupRequest) -> str:
        """
        Generates and saves the Stage 2 delivery OTP hash on the pickup request.
        Returns the plaintext OTP (to be communicated to the NGO or displayed in NGO portal).
        """
        plain_otp, hashed_otp, qr_token = cls.generate_otp()
        request.delivery_otp_hash = hashed_otp
        request.qr_token = qr_token
        request.delivery_attempts_count = 0
        request.delivery_otp_expires_at = utc_now() + timedelta(hours=24)

        db.commit()
        db.refresh(request)
        return plain_otp

    @classmethod
    def verify_pickup_code(
        cls,
        db: Session,
        request_id: int,
        submitted_code: Optional[str] = None,
        user_id: int = 1,
        notes: Optional[str] = None,
        qr_token: Optional[str] = None,
    ) -> PickupRequest:
        """
        Verifies pickup OTP code provided by volunteer at donor handover.
        """
        req = db.query(PickupRequest).filter(PickupRequest.request_id == request_id).with_for_update().first()
        if not req:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pickup request not found.")

        if req.request_status != "assigned":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot verify pickup for request with status '{req.request_status}'. Must be in 'assigned' status."
            )

        if not req.pickup_otp_hash:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No active pickup verification code for this request.")

        # Check maximum failed attempts
        if req.pickup_attempts_count >= 5:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Verification locked: Maximum 5 attempts exceeded. Contact support or request a new code."
            )

        # Check expiration
        now = utc_now()
        # Verify underlying food batch has not expired
        if req.food_batch and req.food_batch.expiry_time:
            batch_exp = to_naive_utc(req.food_batch.expiry_time)
            if batch_exp <= now or req.food_batch.food_status == "expired":
                req.food_batch.food_status = "expired"
                req.request_status = "cancelled"
                db.commit()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot verify pickup: this food batch has already expired.",
                )

        if req.pickup_otp_expires_at and to_naive_utc(req.pickup_otp_expires_at) < now:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Pickup verification code has expired. Please request a new code from the donor."
            )

        # Verify hash or QR token
        is_valid = False
        if qr_token and req.qr_token and qr_token.strip() == req.qr_token.strip():
            is_valid = True
        elif submitted_code:
            submitted_hash = cls.hash_code(submitted_code)
            if submitted_hash == req.pickup_otp_hash:
                is_valid = True

        if not is_valid:
            req.pickup_attempts_count = (req.pickup_attempts_count or 0) + 1
            remaining_attempts = max(0, 5 - req.pickup_attempts_count)
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid pickup code or QR token. {remaining_attempts} attempt(s) remaining."
            )

        # Verification successful: transition to 'collected'
        req.request_status = "collected"
        req.collected_at = now
        req.pickup_otp_hash = None  # Single-use: clear used hash to prevent replay

        # Automatically generate Stage 2 Delivery Code for NGO
        plain_delivery_otp, del_hash, new_qr = cls.generate_otp()
        req.delivery_otp_hash = del_hash
        req.qr_token = new_qr
        req.delivery_attempts_count = 0
        req.delivery_otp_expires_at = now + timedelta(hours=24)

        # Log audit entry
        log_entry = DeliveryLog(
            request_id=req.request_id,
            batch_id=req.batch_id,
            performed_by_user_id=user_id,
            action="pickup_verified_collected",
            notes=notes or "Secure Pickup OTP verified at donor handover. Stage 1 complete.",
            logged_at=now,
        )
        db.add(log_entry)

        # Update batch status
        batch = req.food_batch
        if batch:
            from app.services.allocation_service import AllocationService
            AllocationService.update_batch_derived_status(db, batch)

        # In-app notifications
        from app.services.notification_service import NotificationService
        if batch and batch.donor:
            NotificationService.notify_donor_food_collected(
                db=db,
                donor_user_id=batch.donor.user_id,
                volunteer_name=req.volunteer.volunteer_name if req.volunteer else "Courier",
                food_name=batch.food_name,
                req_id=req.request_id,
            )

        if req.ngo:
            NotificationService.notify_ngo_food_collected(
                db=db,
                ngo_user_id=req.ngo.user_id,
                volunteer_name=req.volunteer.volunteer_name if req.volunteer else "Courier",
                food_name=batch.food_name if batch else "Food",
                req_id=req.request_id,
                delivery_code=plain_delivery_otp,
            )

        db.commit()
        db.refresh(req)
        return req

    @classmethod
    def verify_delivery_code(
        cls,
        db: Session,
        request_id: int,
        submitted_code: Optional[str] = None,
        user_id: int = 1,
        notes: Optional[str] = None,
        qr_token: Optional[str] = None,
    ) -> PickupRequest:
        """
        Verifies delivery OTP code or QR token provided by volunteer at NGO shelter delivery.
        """
        req = db.query(PickupRequest).filter(PickupRequest.request_id == request_id).with_for_update().first()
        if not req:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pickup request not found.")

        if req.request_status != "collected":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot verify delivery for request with status '{req.request_status}'. Food must be in 'collected' status."
            )

        if not req.delivery_otp_hash:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No active delivery verification code for this request.")

        # Check attempts
        if (req.delivery_attempts_count or 0) >= 5:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Verification locked: Maximum 5 attempts exceeded. Contact administrator or recipient NGO."
            )

        # Check expiration
        now = utc_now()
        # Verify underlying food batch has not expired
        if req.food_batch and req.food_batch.expiry_time:
            batch_exp = to_naive_utc(req.food_batch.expiry_time)
            if batch_exp <= now or req.food_batch.food_status == "expired":
                req.food_batch.food_status = "expired"
                req.request_status = "cancelled"
                db.commit()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot verify delivery: this food batch has already expired.",
                )

        if req.delivery_otp_expires_at and to_naive_utc(req.delivery_otp_expires_at) < now:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Delivery verification code has expired. Please ask the recipient NGO for a refreshed code."
            )

        # Verify hash or QR token
        is_valid = False
        if qr_token and req.qr_token and qr_token.strip() == req.qr_token.strip():
            is_valid = True
        elif submitted_code:
            submitted_hash = cls.hash_code(submitted_code)
            if submitted_hash == req.delivery_otp_hash:
                is_valid = True

        if not is_valid:
            req.delivery_attempts_count = (req.delivery_attempts_count or 0) + 1
            remaining_attempts = max(0, 5 - req.delivery_attempts_count)
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid delivery code or QR token. {remaining_attempts} attempt(s) remaining."
            )

        # Verification successful: transition to 'delivered'
        req.request_status = "delivered"
        req.completed_at = now
        req.delivery_otp_hash = None  # Single-use: clear to prevent replay

        # Log audit entry
        log_entry = DeliveryLog(
            request_id=req.request_id,
            batch_id=req.batch_id,
            performed_by_user_id=user_id,
            action="delivery_verified_completed",
            notes=notes or "Secure Delivery OTP verified at NGO shelter. Stage 2 complete.",
            logged_at=now,
        )
        db.add(log_entry)

        # Update batch completion status if all portions are delivered
        batch = req.food_batch
        if batch:
            from app.services.allocation_service import AllocationService
            AllocationService.update_batch_derived_status(db, batch)

        # In-app notifications
        from app.services.notification_service import NotificationService
        if batch and batch.donor and req.ngo:
            NotificationService.notify_donor_food_delivered(
                db=db,
                donor_user_id=batch.donor.user_id,
                ngo_name=req.ngo.ngo_name,
                food_name=batch.food_name,
                req_id=req.request_id,
            )

        if req.ngo:
            NotificationService.notify_ngo_delivery_completed(
                db=db,
                ngo_user_id=req.ngo.user_id,
                food_name=batch.food_name if batch else "Food",
                qty=float(req.requested_quantity),
                unit=req.unit,
                req_id=req.request_id,
            )

        db.commit()
        db.refresh(req)

        return req
