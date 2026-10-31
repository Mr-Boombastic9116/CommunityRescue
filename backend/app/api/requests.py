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
