from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Body, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.user import User
from app.models.volunteer import Volunteer
from app.models.pickup_request import PickupRequest
from app.schemas.pickup_request import PickupRequestResponse
from app.api.deps import require_roles
from app.api.requests import format_request_response
from app.services.workflow_service import WorkflowService
from app.services.expiry_service import process_food_expiries

router = APIRouter(prefix="/volunteer", tags=["Volunteer Tasks"])

class StatusUpdateNote(BaseModel):
    notes: Optional[str] = None
    code: Optional[str] = None
    pickup_code: Optional[str] = None
    delivery_code: Optional[str] = None
    qr_token: Optional[str] = None

class VerifyHandoverPayload(BaseModel):
    code: Optional[str] = None
    qr_token: Optional[str] = None
    notes: Optional[str] = None

class AvailabilityUpdate(BaseModel):
    status: str

@router.get("/tasks/available", response_model=List[PickupRequestResponse])
def get_available_tasks(
    current_user: User = Depends(require_roles(["volunteer"])),
    db: Session = Depends(get_db),
):
    process_food_expiries(db)
    
    # Available tasks are those requested by NGOs but not yet claimed by any volunteer
    tasks = (
        db.query(PickupRequest)
        .filter(
            PickupRequest.request_status == "requested",
            PickupRequest.volunteer_id.is_(None)
        )
        .order_by(PickupRequest.requested_at.asc())
        .all()
    )
    return [format_request_response(t) for t in tasks]

@router.post("/tasks/{request_id}/claim", response_model=PickupRequestResponse)
def claim_task(
    request_id: int,
    current_user: User = Depends(require_roles(["volunteer"])),
    db: Session = Depends(get_db),
):
    volunteer = current_user.volunteer
    if not volunteer:
        raise HTTPException(status_code=400, detail="Volunteer profile not found.")

    process_food_expiries(db)
    updated_req = WorkflowService.claim_pickup_task(db, request_id, volunteer)
    return format_request_response(updated_req)

@router.get("/tasks/assigned", response_model=List[PickupRequestResponse])
def get_assigned_tasks(
    current_user: User = Depends(require_roles(["volunteer"])),
    db: Session = Depends(get_db),
):
    volunteer = current_user.volunteer
    if not volunteer:
        return []

    process_food_expiries(db)

    # Active tasks currently assigned or collected (in-transit)
    tasks = (
        db.query(PickupRequest)
        .filter(
            PickupRequest.volunteer_id == volunteer.volunteer_id,
            PickupRequest.request_status.in_(["assigned", "collected"])
        )
        .order_by(PickupRequest.assigned_at.desc())
        .all()
    )
    return [format_request_response(t) for t in tasks]

@router.get("/tasks/history", response_model=List[PickupRequestResponse])
def get_delivery_history(
    current_user: User = Depends(require_roles(["volunteer"])),
    db: Session = Depends(get_db),
):
    volunteer = current_user.volunteer
    if not volunteer:
        return []

    tasks = (
        db.query(PickupRequest)
        .filter(
            PickupRequest.volunteer_id == volunteer.volunteer_id,
            PickupRequest.request_status.in_(["delivered", "cancelled"])
        )
        .order_by(PickupRequest.updated_at.desc())
        .all()
    )
    return [format_request_response(t) for t in tasks]

@router.post("/tasks/{request_id}/verify-pickup", response_model=PickupRequestResponse)
def verify_pickup_handover(
    request_id: int,
    payload: VerifyHandoverPayload,
    current_user: User = Depends(require_roles(["volunteer"])),
    db: Session = Depends(get_db),
):
    volunteer = current_user.volunteer
    if not volunteer:
        raise HTTPException(status_code=400, detail="Volunteer profile not found.")

    req = db.query(PickupRequest).filter(PickupRequest.request_id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Pickup request not found.")

    if req.volunteer_id != volunteer.volunteer_id:
        raise HTTPException(status_code=403, detail="Access denied: You are not assigned to this pickup task.")

    from app.services.verification_service import VerificationService
    updated_req = VerificationService.verify_pickup_code(
        db=db,
        request_id=request_id,
        submitted_code=payload.code,
        user_id=current_user.user_id,
        notes=payload.notes,
        qr_token=payload.qr_token,
    )
    return format_request_response(updated_req)

@router.post("/tasks/{request_id}/verify-delivery", response_model=PickupRequestResponse)
def verify_delivery_handover(
    request_id: int,
    payload: VerifyHandoverPayload,
    current_user: User = Depends(require_roles(["volunteer"])),
    db: Session = Depends(get_db),
):
    volunteer = current_user.volunteer
    if not volunteer:
        raise HTTPException(status_code=400, detail="Volunteer profile not found.")

    req = db.query(PickupRequest).filter(PickupRequest.request_id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Pickup request not found.")

    if req.volunteer_id != volunteer.volunteer_id:
        raise HTTPException(status_code=403, detail="Access denied: You are not assigned to this delivery task.")

    from app.services.verification_service import VerificationService
    updated_req = VerificationService.verify_delivery_code(
        db=db,
        request_id=request_id,
        submitted_code=payload.code,
        user_id=current_user.user_id,
        notes=payload.notes,
        qr_token=payload.qr_token,
    )
    return format_request_response(updated_req)

@router.post("/tasks/{request_id}/collect", response_model=PickupRequestResponse)
def collect_food(
    request_id: int,
    payload: StatusUpdateNote = Body(default=StatusUpdateNote()),
    current_user: User = Depends(require_roles(["volunteer"])),
    db: Session = Depends(get_db),
):
    volunteer = current_user.volunteer
    if not volunteer:
        raise HTTPException(status_code=400, detail="Volunteer profile not found.")

    code_to_use = payload.code or payload.pickup_code
    updated_req = WorkflowService.mark_food_collected(
        db=db,
        request_id=request_id,
        volunteer=volunteer,
        notes=payload.notes,
        code=code_to_use,
        qr_token=payload.qr_token,
    )
    return format_request_response(updated_req)

@router.post("/tasks/{request_id}/deliver", response_model=PickupRequestResponse)
def complete_delivery(
    request_id: int,
    payload: StatusUpdateNote = Body(default=StatusUpdateNote()),
    current_user: User = Depends(require_roles(["volunteer"])),
    db: Session = Depends(get_db),
):
    volunteer = current_user.volunteer
    if not volunteer:
        raise HTTPException(status_code=400, detail="Volunteer profile not found.")

    code_to_use = payload.code or payload.delivery_code
    updated_req = WorkflowService.mark_delivery_completed(
        db=db,
        request_id=request_id,
        volunteer=volunteer,
        notes=payload.notes,
        code=code_to_use,
        qr_token=payload.qr_token,
    )
    return format_request_response(updated_req)

@router.put("/availability")
def set_availability(
    payload: AvailabilityUpdate,
    current_user: User = Depends(require_roles(["volunteer"])),
    db: Session = Depends(get_db),
):
    if payload.status not in ["available", "busy", "offline"]:
        raise HTTPException(
            status_code=400,
            detail="Status must be one of: 'available', 'busy', 'offline'",
        )

    volunteer = current_user.volunteer
    if not volunteer:
        raise HTTPException(status_code=400, detail="Volunteer profile not found.")

    volunteer.availability_status = payload.status
    db.commit()
    return {"message": "Availability updated successfully", "availability_status": volunteer.availability_status}

