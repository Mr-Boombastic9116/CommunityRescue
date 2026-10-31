from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.user import User
from app.models.ngo import NGOPartner
from app.models.food_batch import FoodBatch
from app.models.pickup_request import PickupRequest
from app.models.delivery_log import DeliveryLog
from app.models.notification import Notification
from app.schemas.pickup_request import (
    PickupRequestCreate,
    PickupRequestResponse,
    PickupRequestDetailResponse,
    DeliveryLogResponse,
)
from app.api.deps import get_current_user, require_roles
from app.api.donations import format_batch_response
from app.services.expiry_service import process_food_expiries
from app.services.allocation_service import AllocationService
from app.utils.dates import utc_now, to_naive_utc

router = APIRouter(prefix="/requests", tags=["NGO Requests"])

def format_request_response(req: PickupRequest) -> PickupRequestResponse:
    batch_resp = format_batch_response(req.food_batch) if req.food_batch else None
    return PickupRequestResponse(
        request_id=req.request_id,
        batch_id=req.batch_id,
        ngo_id=req.ngo_id,
        ngo_name=req.ngo.ngo_name if req.ngo else None,
        ngo_phone=req.ngo.phone if req.ngo else None,
        ngo_address=req.ngo.address if req.ngo else None,
        volunteer_id=req.volunteer_id,
        volunteer_name=req.volunteer.volunteer_name if req.volunteer else None,
        volunteer_phone=req.volunteer.phone if req.volunteer else None,
        requested_quantity=float(req.requested_quantity) if req.requested_quantity is not None else (float(req.food_batch.quantity) if req.food_batch else 0.0),
        unit=req.unit or (req.food_batch.unit if req.food_batch else ""),
        request_status=req.request_status,
        requested_at=req.requested_at,
        assigned_at=req.assigned_at,
        collected_at=req.collected_at,
        completed_at=req.completed_at,
        updated_at=req.updated_at,
        food_batch=batch_resp,
    )

@router.post("", response_model=PickupRequestResponse, status_code=status.HTTP_201_CREATED)
def create_request(
    req_in: PickupRequestCreate,
    current_user: User = Depends(require_roles(["ngo"])),
    db: Session = Depends(get_db),
):
    ngo = current_user.ngo
    if not ngo:
        raise HTTPException(status_code=400, detail="NGO profile not found for this user.")

    process_food_expiries(db)

    # Determine requested quantity (defaults to remaining available quantity if not specified)
    if req_in.requested_quantity is not None:
        requested_qty = Decimal(str(req_in.requested_quantity))
    else:
        batch_preview = db.query(FoodBatch).filter(FoodBatch.batch_id == req_in.batch_id).first()
        if not batch_preview:
            raise HTTPException(status_code=404, detail="Food batch not found.")
        _, _, rem = AllocationService.calculate_remaining_quantity(db, req_in.batch_id)
        if rem <= Decimal("0.0"):
            raise HTTPException(status_code=400, detail="Cannot request food: no remaining quantity available.")
        requested_qty = rem

    # Use AllocationService for atomic check, validation, and reservation
    batch = AllocationService.allocate_quantity_atomic(
        db=db,
        batch_id=req_in.batch_id,
        requested_quantity=requested_qty,
    )

    now = utc_now()
    try:
        new_request = PickupRequest(
            batch_id=batch.batch_id,
            ngo_id=ngo.ngo_id,
            requested_quantity=requested_qty,
            unit=batch.unit,
            request_status="requested",
            requested_at=now,
        )
        db.add(new_request)
        db.flush()

        log = DeliveryLog(
            request_id=new_request.request_id,
            performed_by_user_id=current_user.user_id,
            action="FOOD_REQUESTED",
            notes=req_in.notes or f"Requested {req_in.requested_quantity} {batch.unit} for immediate distribution.",
            logged_at=now,
        )
        db.add(log)

        # Notify donor
        if batch.donor:
            db.add(
                Notification(
                    user_id=batch.donor.user_id,
                    title="Donation Requested!",
                    message=f"{ngo.ngo_name} has requested {req_in.requested_quantity} {batch.unit} of your donation '{batch.food_name}'. Waiting for volunteer pickup.",
                )
            )

        db.commit()
        db.refresh(new_request)
        return format_request_response(new_request)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to submit request: {str(e)}")

@router.get("/my", response_model=List[PickupRequestResponse])
def get_my_requests(
    current_user: User = Depends(require_roles(["ngo"])),
    db: Session = Depends(get_db),
):
    ngo = current_user.ngo
    if not ngo:
        return []

    process_food_expiries(db)

    requests = (
        db.query(PickupRequest)
        .filter(PickupRequest.ngo_id == ngo.ngo_id)
        .order_by(PickupRequest.requested_at.desc())
        .all()
    )
    return [format_request_response(r) for r in requests]

@router.get("/{request_id}", response_model=PickupRequestDetailResponse)
def get_request_detail(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    process_food_expiries(db)

    req = db.query(PickupRequest).filter(PickupRequest.request_id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Pickup request not found.")

    # Access control: NGO can see their own, Volunteer can see assigned or available, Donor can see if it's their batch
    is_owner_ngo = current_user.role == "ngo" and current_user.ngo and current_user.ngo.ngo_id == req.ngo_id
    is_batch_donor = current_user.role == "donor" and current_user.donor and current_user.donor.donor_id == req.food_batch.donor_id
    is_volunteer = current_user.role == "volunteer"

    if not (is_owner_ngo or is_batch_donor or is_volunteer):
        raise HTTPException(status_code=403, detail="Access denied: you cannot view details of this request.")

    base_resp = format_request_response(req)

    logs = []
    for log in req.delivery_logs:
        logs.append(
            DeliveryLogResponse(
                log_id=log.log_id,
                request_id=log.request_id,
                performed_by_user_id=log.performed_by_user_id,
                performer_name=log.performed_by_user.name if log.performed_by_user else "System",
                action=log.action,
                notes=log.notes,
                logged_at=log.logged_at,
            )
        )

    return PickupRequestDetailResponse(
        **base_resp.model_dump(),
        delivery_logs=logs,
    )

@router.post("/{request_id}/cancel", response_model=PickupRequestResponse)
def cancel_request(
    request_id: int,
    current_user: User = Depends(require_roles(["ngo"])),
    db: Session = Depends(get_db),
):
    ngo = current_user.ngo
    req = db.query(PickupRequest).filter(PickupRequest.request_id == request_id).with_for_update().first()
    if not req:
        raise HTTPException(status_code=404, detail="Pickup request not found.")

    if req.ngo_id != ngo.ngo_id:
        raise HTTPException(status_code=403, detail="You do not have permission to cancel this request.")

    if req.request_status != "requested":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel request in '{req.request_status}' status. It may already be assigned or in transit.",
        )

    batch = db.query(FoodBatch).filter(FoodBatch.batch_id == req.batch_id).with_for_update().first()
    now = utc_now()

    req.request_status = "cancelled"
    log = DeliveryLog(
        request_id=req.request_id,
        performed_by_user_id=current_user.user_id,
        action="REQUEST_CANCELLED",
        notes=f"Request cancelled by NGO {ngo.ngo_name}. Quantity {req.requested_quantity} {req.unit} released.",
        logged_at=now,
    )
    db.add(log)

    if batch:
        AllocationService.update_batch_derived_status(db, batch)

    try:
        db.commit()
        db.refresh(req)
        return format_request_response(req)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to cancel request: {str(e)}")

@router.get("/{request_id}/timeline")
def get_request_timeline(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.services.timeline_service import TimelineService
    req = db.query(PickupRequest).filter(PickupRequest.request_id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Pickup request not found.")

    is_owner_ngo = current_user.role == "ngo" and current_user.ngo and current_user.ngo.ngo_id == req.ngo_id
    is_batch_donor = current_user.role == "donor" and current_user.donor and req.food_batch and current_user.donor.donor_id == req.food_batch.donor_id
    is_volunteer = current_user.role == "volunteer"
    is_admin = current_user.role == "admin"
    if not (is_owner_ngo or is_batch_donor or is_volunteer or is_admin):
        raise HTTPException(status_code=403, detail="Access denied: You cannot view the timeline for this request.")

    timeline = TimelineService.get_request_timeline(db, request_id, requesting_user=current_user)
    return {"request_id": request_id, "stages": timeline}

@router.get("/{request_id}/handover-code")
def get_handover_code(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns the secure handover code and QR token for the authorized party:
    - If donor and status is 'assigned': returns Stage 1 Pickup code.
    - If NGO and status is 'collected': returns Stage 2 Delivery code.
    - Volunteer or unauthorized user: HTTP 403 Forbidden.
    """
    req = db.query(PickupRequest).filter(PickupRequest.request_id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Pickup request not found.")

    if current_user.role == "volunteer":
        raise HTTPException(
            status_code=403,
            detail="Couriers cannot inspect handover codes directly. Obtain the code in person from the donor or NGO."
        )

    is_donor = current_user.role == "donor" and current_user.donor and req.food_batch and current_user.donor.donor_id == req.food_batch.donor_id
    is_ngo = current_user.role == "ngo" and current_user.ngo and current_user.ngo.ngo_id == req.ngo_id

    if not (is_donor or is_ngo):
        raise HTTPException(status_code=403, detail="Access denied: You are not authorized to view this handover code.")

    import re
    if is_donor:
        if req.request_status != "assigned":
            return {
                "type": "pickup",
                "request_id": req.request_id,
                "status": req.request_status,
                "handover_code": None,
                "message": f"Pickup code is not active (current status: '{req.request_status}')"
            }

        notif = db.query(Notification).filter(
            Notification.user_id == current_user.user_id,
            Notification.reference_id == req.request_id,
            Notification.notification_type.in_(["pickup_code", "donor_volunteer_assigned"])
        ).order_by(Notification.created_at.desc()).first()

        code = None
        if notif and notif.message:
            m = re.search(r'\b\d{6}\b', notif.message)
            if m:
                code = m.group(0)

        if not code or not req.pickup_otp_hash:
            from app.services.verification_service import VerificationService
            code = VerificationService.setup_pickup_verification(db, req)
            from app.services.notification_service import NotificationService
            NotificationService.notify_donor_volunteer_assigned(
                db, current_user.user_id, req.volunteer.volunteer_name if req.volunteer else "Courier", req.food_batch.food_name if req.food_batch else "Food", req.request_id, code
            )

        return {
            "type": "pickup",
            "request_id": req.request_id,
            "status": req.request_status,
            "handover_code": code,
            "qr_token": req.qr_token,
            "expires_at": req.pickup_otp_expires_at.isoformat() if req.pickup_otp_expires_at else None,
            "attempts_remaining": max(0, 5 - (req.pickup_attempts_count or 0)),
            "instructions": "Provide this 6-digit code or QR code to the volunteer courier when handing over the food.",
        }

    if is_ngo:
        if req.request_status != "collected":
            return {
                "type": "delivery",
                "request_id": req.request_id,
                "status": req.request_status,
                "handover_code": None,
                "message": f"Delivery code is not active (current status: '{req.request_status}')"
            }

        notif = db.query(Notification).filter(
            Notification.user_id == current_user.user_id,
            Notification.reference_id == req.request_id,
            Notification.notification_type.in_(["delivery_code", "ngo_food_collected"])
        ).order_by(Notification.created_at.desc()).first()

        code = None
        if notif and notif.message:
            m = re.search(r'\b\d{6}\b', notif.message)
            if m:
                code = m.group(0)

        if not code or not req.delivery_otp_hash:
            from app.services.verification_service import VerificationService
            code = VerificationService.setup_delivery_verification(db, req)
            from app.services.notification_service import NotificationService
            NotificationService.notify_ngo_food_collected(
                db, current_user.user_id, req.volunteer.volunteer_name if req.volunteer else "Courier", req.food_batch.food_name if req.food_batch else "Food", req.request_id, code
            )

        return {
            "type": "delivery",
            "request_id": req.request_id,
            "status": req.request_status,
            "handover_code": code,
            "qr_token": req.qr_token,
            "expires_at": req.delivery_otp_expires_at.isoformat() if req.delivery_otp_expires_at else None,
            "attempts_remaining": max(0, 5 - (req.delivery_attempts_count or 0)),
            "instructions": "Provide this 6-digit code or QR code to the volunteer courier when receiving the food at your shelter.",
        }

@router.post("/{request_id}/refresh-handover-code")
def refresh_handover_code(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Regenerates a fresh handover code if expired or locked.
    """
    req = db.query(PickupRequest).filter(PickupRequest.request_id == request_id).with_for_update().first()
    if not req:
        raise HTTPException(status_code=404, detail="Pickup request not found.")

    is_donor = current_user.role == "donor" and current_user.donor and req.food_batch and current_user.donor.donor_id == req.food_batch.donor_id
    is_ngo = current_user.role == "ngo" and current_user.ngo and current_user.ngo.ngo_id == req.ngo_id

    from app.services.verification_service import VerificationService
    from app.services.notification_service import NotificationService

    if is_donor:
        if req.request_status != "assigned":
            raise HTTPException(status_code=400, detail="Cannot refresh pickup code: Task is not in 'assigned' status.")
        code = VerificationService.setup_pickup_verification(db, req)
        NotificationService.notify_donor_volunteer_assigned(
            db, current_user.user_id, req.volunteer.volunteer_name if req.volunteer else "Courier", req.food_batch.food_name if req.food_batch else "Food", req.request_id, code
        )
        return {
            "handover_code": code,
            "type": "pickup",
            "qr_token": req.qr_token,
            "message": "New pickup verification code generated.",
        }

    if is_ngo:
        if req.request_status != "collected":
            raise HTTPException(status_code=400, detail="Cannot refresh delivery code: Food is not in 'collected' (in transit) status.")
        code = VerificationService.setup_delivery_verification(db, req)
        NotificationService.notify_ngo_food_collected(
            db, current_user.user_id, req.volunteer.volunteer_name if req.volunteer else "Courier", req.food_batch.food_name if req.food_batch else "Food", req.request_id, code
        )
        return {
            "handover_code": code,
            "type": "delivery",
            "qr_token": req.qr_token,
            "message": "New delivery verification code generated.",
        }

    raise HTTPException(status_code=403, detail="Access denied.")
