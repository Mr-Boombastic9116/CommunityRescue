from datetime import datetime, timedelta
from typing import List, Optional
from decimal import Decimal
import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database.session import get_db
from app.models.user import User
from app.models.food_batch import FoodBatch
from app.models.donor import Donor
from app.models.pickup_request import PickupRequest
from app.models.delivery_log import DeliveryLog
from app.schemas.food_batch import (
    FoodBatchCreate,
    FoodBatchUpdate,
    FoodBatchResponse,
    FoodBatchDetailResponse,
)
from app.api.deps import get_current_user, require_roles
from app.services.expiry_service import calculate_expiry_metadata, process_food_expiries
from app.services.expiry_validation_service import ExpiryValidationService
from app.services.allocation_service import AllocationService
from app.schemas.ai import CalculateExpiryRequest, CalculateExpiryResponse
from app.utils.dates import utc_now, to_naive_utc, format_utc_iso

router = APIRouter(prefix="/donations", tags=["Donations"])

@router.post("/upload-image")
async def upload_donation_photo(
    image: UploadFile = File(...),
    current_user: User = Depends(require_roles(["donor"])),
):
    """
    Upload an ordinary food donation photograph for display on marketplace cards.
    Validates format (JPEG, PNG, WebP) and size (<= 10MB).
    """
    allowed_types = ["image/jpeg", "image/png", "image/webp"]
    if image.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported image type: '{image.content_type}'. Allowed: JPEG, PNG, WebP.",
        )
    image_bytes = await image.read()
    if len(image_bytes) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Image file is empty.")
    if len(image_bytes) > 10 * 1024 * 1024:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Image size exceeds 10 MB limit.")

    uploads_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "uploads")
    os.makedirs(uploads_dir, exist_ok=True)
    ext = ".jpg" if "jpeg" in (image.content_type or "") else ".png" if "png" in (image.content_type or "") else ".webp"
    filename = f"donation_{uuid.uuid4().hex[:12]}{ext}"
    file_path = os.path.join(uploads_dir, filename)

    with open(file_path, "wb") as f:
        f.write(image_bytes)

    return {"image_url": f"/uploads/{filename}"}

@router.post("/calculate-expiry", response_model=CalculateExpiryResponse)
def calculate_expiry_endpoint(
    payload: CalculateExpiryRequest,
    db: Session = Depends(get_db),
):
    """
    Calculates approved maximum holding hours and statutory maximum expiry
    from curated FSSAI food safety rules for the donor workflow.
    """
    try:
        prep_at = to_naive_utc(payload.prepared_at)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid prepared_at format: {e}")

    pkg_time = None
    if payload.packaging_expiry:
        try:
            pkg_time = to_naive_utc(payload.packaging_expiry)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid packaging_expiry format: {e}")
    
    validation = ExpiryValidationService.validate_food_expiry(
        db=db,
        food_name=payload.food_name,
        food_category=payload.food_category,
        prepared_at=prep_at,
        user_expiry=prep_at + timedelta(days=365),
        storage_condition=payload.storage_condition,
        packaging_expiry=pkg_time,
    )
    rule = ExpiryValidationService.find_matching_rule(
        db=db,
        food_category=payload.food_category,
        storage_condition=payload.storage_condition,
        food_name=payload.food_name,
    )

    if validation.requires_manual_verification or not rule:
        return CalculateExpiryResponse(
            food_category=payload.food_category,
            storage_condition=payload.storage_condition,
            max_holding_hours=None,
            approved_maximum_expiry=None,
            rule_applied=None,
            rule_source=None,
            rule_clause=None,
            requires_manual_verification=True,
            verification_reason="No verified FSSAI safety rule found for this food category and storage condition. Manual verification required.",
        )

    return CalculateExpiryResponse(
        food_category=payload.food_category,
        storage_condition=payload.storage_condition,
        max_holding_hours=validation.max_permitted_hours,
        approved_maximum_expiry=format_utc_iso(validation.max_allowed_expiry) if validation.max_allowed_expiry else None,
        rule_applied=validation.rule_applied,
        rule_source=validation.source_name,
        rule_clause=rule.rule_version if rule else None,
        requires_manual_verification=False,
    )

def format_batch_response(batch: FoodBatch, db: Optional[Session] = None) -> FoodBatchResponse:
    remaining_hours, is_close, urgency_level = calculate_expiry_metadata(batch)
    
    total_qty = float(batch.quantity)
    allocated_qty = 0.0
    remaining_qty = total_qty

    if db is not None:
        _, allocated_dec, remaining_dec = AllocationService.calculate_remaining_quantity(db, batch.batch_id)
        allocated_qty = float(allocated_dec)
        remaining_qty = float(remaining_dec)
    elif hasattr(batch, "pickup_requests") and batch.pickup_requests:
        from app.services.allocation_service import ALLOCATED_REQUEST_STATUSES
        allocated_sum = sum(
            float(r.requested_quantity)
            for r in batch.pickup_requests
            if r.request_status in ALLOCATED_REQUEST_STATUSES
        )
        allocated_qty = allocated_sum
        remaining_qty = max(0.0, total_qty - allocated_sum)

    # Determine adjustment reason if adjusted
    reason = None
    if batch.expiry_validation_status == "adjusted":
        reason = f"Adjusted to safety threshold based on {batch.expiry_rule_applied or 'food safety guidelines'}."
    elif batch.expiry_validation_status == "manual_verification_required":
        reason = "No certified rule found for this storage condition; requires explicit verification."

    max_holding_hours = None
    approved_maximum_expiry = None
    if db is not None and batch.prepared_at:
        rule = ExpiryValidationService.find_matching_rule(
            db=db,
            food_category=batch.food_category,
            storage_condition=batch.storage_condition or "ambient",
            food_name=batch.food_name,
        )
        if rule and rule.max_holding_hours:
            max_holding_hours = float(rule.max_holding_hours)
            approved_maximum_expiry = to_naive_utc(batch.prepared_at) + timedelta(hours=max_holding_hours)
            if batch.packaging_expiry_time:
                pkg_exp = to_naive_utc(batch.packaging_expiry_time)
                if pkg_exp < approved_maximum_expiry:
                    approved_maximum_expiry = pkg_exp

    return FoodBatchResponse(
        batch_id=batch.batch_id,
        donor_id=batch.donor_id,
        donor_name=batch.donor.donor_name if batch.donor else None,
        donor_phone=batch.donor.phone if batch.donor else None,
        food_name=batch.food_name,
        food_description=batch.food_description,
        food_category=batch.food_category,
        quantity=total_qty,
        donated_quantity=total_qty,
        allocated_quantity=allocated_qty,
        remaining_quantity=remaining_qty,
        unit=batch.unit,
        prepared_at=batch.prepared_at,
        user_expiry_time=batch.user_expiry_time or batch.expiry_time,
        effective_expiry_time=batch.effective_expiry_time or batch.expiry_time,
        expiry_time=batch.expiry_time,
        packaging_expiry_time=batch.packaging_expiry_time,
        storage_condition=batch.storage_condition or "ambient",
        storage_temperature=float(batch.storage_temperature) if batch.storage_temperature else None,
        expiry_validation_status=batch.expiry_validation_status or "verified",
        expiry_rule_applied=batch.expiry_rule_applied,
        expiry_adjustment_reason=reason,
        image_url=batch.image_url,
        food_status=batch.food_status,
        pickup_address=batch.pickup_address,
        latitude=float(batch.latitude) if batch.latitude else None,
        longitude=float(batch.longitude) if batch.longitude else None,
        created_at=batch.created_at,
        updated_at=batch.updated_at,
        remaining_hours=remaining_hours,
        is_close_to_expiry=is_close,
        urgency_level=urgency_level,
        max_holding_hours=max_holding_hours,
        approved_maximum_expiry=approved_maximum_expiry,
    )

@router.post("", response_model=FoodBatchResponse, status_code=status.HTTP_201_CREATED)
def create_donation(
    batch_in: FoodBatchCreate,
    current_user: User = Depends(require_roles(["donor"])),
    db: Session = Depends(get_db),
):
    donor = current_user.donor
    if not donor:
        raise HTTPException(status_code=400, detail="Donor profile not configured for this user.")

    # Validation: Expiry time must be strictly after prepared_at
    prep_at = to_naive_utc(batch_in.prepared_at)
    user_exp_time = to_naive_utc(batch_in.expiry_time)

    if user_exp_time <= prep_at:
        raise HTTPException(
            status_code=400,
            detail="Expiry time must be strictly later than preparation time.",
        )

    # Validation: Expiry time must be in the future
    if user_exp_time <= utc_now():
        raise HTTPException(
            status_code=400,
            detail="Expiry time must be in the future.",
        )

    # Mandatory Food Safety Expiry Validation (FSSAI Rules)
    validation = ExpiryValidationService.validate_food_expiry(
        db=db,
        food_name=batch_in.food_name,
        food_category=batch_in.food_category,
        prepared_at=prep_at,
        user_expiry=user_exp_time,
        storage_condition=batch_in.storage_condition,
        packaging_expiry=batch_in.packaging_expiry_time,
    )

    if validation.is_exceeded:
        raise HTTPException(
            status_code=400,
            detail=validation.error_message,
        )

    new_batch = FoodBatch(
        donor_id=donor.donor_id,
        food_name=batch_in.food_name.strip(),
        food_description=batch_in.food_description.strip() if batch_in.food_description else None,
        food_category=batch_in.food_category.strip(),
        quantity=batch_in.quantity,
        unit=batch_in.unit.strip(),
        prepared_at=prep_at,
        user_expiry_time=user_exp_time,
        effective_expiry_time=validation.effective_expiry,
        expiry_time=validation.effective_expiry,
        packaging_expiry_time=batch_in.packaging_expiry_time,
        storage_condition=batch_in.storage_condition,
        storage_temperature=batch_in.storage_temperature,
        expiry_validation_status=validation.validation_status,
        expiry_rule_applied=validation.rule_applied,
        image_url=batch_in.image_url,
        food_status="pending_verification" if validation.requires_manual_verification else "available",
        pickup_address=batch_in.pickup_address.strip(),
        latitude=batch_in.latitude,
        longitude=batch_in.longitude,
    )
    db.add(new_batch)
    db.commit()
    db.refresh(new_batch)

    return format_batch_response(new_batch, db=db)

@router.get("", response_model=List[FoodBatchResponse])
def list_available_donations(
    search: Optional[str] = Query(None, description="Search by food name or category"),
    category: Optional[str] = Query(None, description="Filter by category"),
    food_status: Optional[str] = Query("available", description="Filter by status (default available)"),
    only_urgent: bool = Query(False, description="Filter items expiring in < 4 hours"),
    db: Session = Depends(get_db),
):
    # Run dynamic expiry check before serving
    process_food_expiries(db)

    query = db.query(FoodBatch)
    if food_status == "available":
        # When querying available donations, include both fully available and partially reserved
        query = query.filter(FoodBatch.food_status.in_(["available", "partially_reserved"]))
    elif food_status and food_status.lower() != "all":
        query = query.filter(FoodBatch.food_status == food_status)

    if category and category.lower() != "all":
        query = query.filter(FoodBatch.food_category == category)

    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                FoodBatch.food_name.ilike(search_term),
                FoodBatch.food_category.ilike(search_term),
                FoodBatch.pickup_address.ilike(search_term),
                FoodBatch.food_description.ilike(search_term),
            )
        )

    batches = query.order_by(FoodBatch.expiry_time.asc()).all()
    results = [format_batch_response(b, db=db) for b in batches]

    if only_urgent:
        results = [r for r in results if r.is_close_to_expiry]

    return results

@router.get("/my", response_model=List[FoodBatchResponse])
def list_my_donations(
    current_user: User = Depends(require_roles(["donor"])),
    db: Session = Depends(get_db),
):
    process_food_expiries(db)
    donor = current_user.donor
    if not donor:
        return []

    batches = (
        db.query(FoodBatch)
        .filter(FoodBatch.donor_id == donor.donor_id)
        .order_by(FoodBatch.created_at.desc())
        .all()
    )
    return [format_batch_response(b, db=db) for b in batches]

@router.get("/{batch_id}", response_model=FoodBatchDetailResponse)
def get_donation_detail(batch_id: int, db: Session = Depends(get_db)):
    process_food_expiries(db)
    batch = db.query(FoodBatch).filter(FoodBatch.batch_id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Food batch not found.")

    base_resp = format_batch_response(batch, db=db)
    
    requests_data = []
    for req in batch.pickup_requests:
        requests_data.append({
            "request_id": req.request_id,
            "ngo_id": req.ngo_id,
            "ngo_name": req.ngo.ngo_name if req.ngo else "Unknown NGO",
            "requested_quantity": float(req.requested_quantity),
            "unit": req.unit,
            "request_status": req.request_status,
            "volunteer_name": req.volunteer.volunteer_name if req.volunteer else None,
            "requested_at": req.requested_at.isoformat() if req.requested_at else None,
            "assigned_at": req.assigned_at.isoformat() if req.assigned_at else None,
            "collected_at": req.collected_at.isoformat() if req.collected_at else None,
            "completed_at": req.completed_at.isoformat() if req.completed_at else None,
        })

    return FoodBatchDetailResponse(
        **base_resp.model_dump(),
        requests=requests_data,
    )

@router.put("/{batch_id}", response_model=FoodBatchResponse)
def update_donation(
    batch_id: int,
    batch_update: FoodBatchUpdate,
    current_user: User = Depends(require_roles(["donor"])),
    db: Session = Depends(get_db),
):
    donor = current_user.donor
    batch = db.query(FoodBatch).filter(FoodBatch.batch_id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Food batch not found.")

    if batch.donor_id != donor.donor_id:
        raise HTTPException(status_code=403, detail="You do not have permission to modify this donation.")

    now = utc_now()
    if to_naive_utc(batch.expiry_time) <= now or batch.food_status == "expired":
        raise HTTPException(
            status_code=400,
            detail="Cannot edit donation batch that has already expired.",
        )

    # Status check: only eligible donations (available or partially_reserved) can be edited
    if batch.food_status not in ["available", "partially_reserved"]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot edit donation that is already '{batch.food_status}'.",
        )

    if batch_update.food_name is not None:
        batch.food_name = batch_update.food_name.strip()
    if batch_update.food_description is not None:
        batch.food_description = batch_update.food_description.strip()
    if batch_update.food_category is not None:
        batch.food_category = batch_update.food_category.strip()
    if batch_update.quantity is not None:
        batch.quantity = batch_update.quantity
    if batch_update.unit is not None:
        batch.unit = batch_update.unit.strip()
    if batch_update.prepared_at is not None:
        batch.prepared_at = batch_update.prepared_at
    if batch_update.storage_condition is not None:
        batch.storage_condition = batch_update.storage_condition
    if batch_update.storage_temperature is not None:
        batch.storage_temperature = batch_update.storage_temperature
    if batch_update.packaging_expiry_time is not None:
        batch.packaging_expiry_time = batch_update.packaging_expiry_time
    if batch_update.image_url is not None:
        batch.image_url = batch_update.image_url
    if batch_update.pickup_address is not None:
        batch.pickup_address = batch_update.pickup_address.strip()
    if batch_update.latitude is not None:
        batch.latitude = batch_update.latitude
    if batch_update.longitude is not None:
        batch.longitude = batch_update.longitude

    # Re-validate expiry if user_expiry or storage or prep changed
    user_exp = batch_update.expiry_time or batch.user_expiry_time or batch.expiry_time
    user_exp = to_naive_utc(user_exp)

    if user_exp <= to_naive_utc(batch.prepared_at):
        raise HTTPException(status_code=400, detail="Expiry time must be strictly later than preparation time.")

    if user_exp <= now:
        raise HTTPException(status_code=400, detail="Expiry time must be in the future.")

    validation = ExpiryValidationService.validate_food_expiry(
        db=db,
        food_name=batch.food_name,
        food_category=batch.food_category,
        prepared_at=batch.prepared_at,
        user_expiry=user_exp,
        storage_condition=batch.storage_condition,
        packaging_expiry=batch.packaging_expiry_time,
    )

    if validation.is_exceeded:
        raise HTTPException(
            status_code=400,
            detail=validation.error_message,
        )

    batch.user_expiry_time = user_exp
    batch.effective_expiry_time = validation.effective_expiry
    batch.expiry_time = validation.effective_expiry
    batch.expiry_validation_status = validation.validation_status
    batch.expiry_rule_applied = validation.rule_applied

    AllocationService.update_batch_derived_status(db, batch)

    db.commit()
    db.refresh(batch)
    return format_batch_response(batch, db=db)

@router.post("/{batch_id}/cancel", response_model=FoodBatchResponse)
def cancel_donation(
    batch_id: int,
    current_user: User = Depends(require_roles(["donor"])),
    db: Session = Depends(get_db),
):
    donor = current_user.donor
    batch = db.query(FoodBatch).filter(FoodBatch.batch_id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Food batch not found.")

    if batch.donor_id != donor.donor_id:
        raise HTTPException(status_code=403, detail="You do not have permission to cancel this donation.")

    if batch.food_status not in ["available"]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel donation in '{batch.food_status}' status. It may have already been partially requested or claimed.",
        )

    batch.food_status = "cancelled"
    db.commit()
    db.refresh(batch)
    return format_batch_response(batch, db=db)

@router.get("/{batch_id}/recommended-ngos")
def get_recommended_ngos_for_donation(
    batch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Ranks verified NGOs using smart multi-factor matching engine:
    30% Distance, 25% Category compatibility, 20% Capacity, 15% Expiry urgency, 10% Operating availability.
    """
    batch = db.query(FoodBatch).filter(FoodBatch.batch_id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Food batch not found.")

    if current_user.role == "donor" and current_user.donor and current_user.donor.donor_id != batch.donor_id:
        raise HTTPException(status_code=403, detail="You do not have permission to view recommendations for this batch.")

    from app.services.matching_service import SmartMatchingService
    recommendations = SmartMatchingService.match_ngos_for_donation(db=db, batch_id=batch_id)
    return {
        "batch_id": batch_id,
        "food_name": batch.food_name,
        "recommendations": recommendations,
    }

@router.get("/{batch_id}/timeline")
def get_batch_lifecycle_timeline(
    batch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns complete chronological 9-stage lifecycle events for this food donation batch.
    """
    batch = db.query(FoodBatch).filter(FoodBatch.batch_id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Food batch not found.")

    from app.services.timeline_service import TimelineService
    events = TimelineService.get_batch_timeline(db=db, batch_id=batch_id, requesting_user=current_user)
    return {
        "batch_id": batch_id,
        "food_name": batch.food_name,
        "events": events,
    }
