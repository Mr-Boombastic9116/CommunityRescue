from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.food_batch import FoodBatchResponse

class PickupRequestCreate(BaseModel):
    batch_id: int
    requested_quantity: Optional[float] = Field(None, gt=0, description="Quantity requested by the NGO. Defaults to full remaining quantity if omitted.")
    notes: Optional[str] = None

class PickupRequestResponse(BaseModel):
    request_id: int
    batch_id: int
    ngo_id: int
    ngo_name: Optional[str] = None
    ngo_phone: Optional[str] = None
    ngo_address: Optional[str] = None
    volunteer_id: Optional[int] = None
    volunteer_name: Optional[str] = None
    volunteer_phone: Optional[str] = None
    requested_quantity: float
    unit: str
    request_status: str
    requested_at: datetime
    assigned_at: Optional[datetime] = None
    collected_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    updated_at: datetime
    food_batch: Optional[FoodBatchResponse] = None
    pickup_code: Optional[str] = None
    delivery_code: Optional[str] = None
    qr_token: Optional[str] = None
    pickup_attempts_count: Optional[int] = 0
    delivery_attempts_count: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)

class DeliveryLogResponse(BaseModel):
    log_id: int
    request_id: int
    performed_by_user_id: Optional[int] = None
    performer_name: Optional[str] = None
    action: str
    notes: Optional[str] = None
    logged_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PickupRequestDetailResponse(PickupRequestResponse):
    delivery_logs: List[DeliveryLogResponse] = []
