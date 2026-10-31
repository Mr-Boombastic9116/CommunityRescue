from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, model_validator, ConfigDict, field_serializer
from app.utils.dates import to_naive_utc, utc_now, format_utc_iso

class FoodBatchCreate(BaseModel):
    food_name: str = Field(..., min_length=2, max_length=255)
    food_description: Optional[str] = None
    food_category: str = Field(..., min_length=2, max_length=100)
    quantity: float = Field(..., gt=0)
    unit: str = Field(..., min_length=1, max_length=50)
    prepared_at: datetime
    expiry_time: datetime
    packaging_expiry_time: Optional[datetime] = None
    storage_condition: str = Field("ambient", max_length=50)  # 'ambient', 'refrigerated', 'frozen', 'hot_holding'
    storage_temperature: Optional[float] = None
    pickup_address: str = Field(..., min_length=3)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    image_url: Optional[str] = None

    @model_validator(mode="after")
    def validate_expiry(self):
        self.prepared_at = to_naive_utc(self.prepared_at)
        self.expiry_time = to_naive_utc(self.expiry_time)
        if self.packaging_expiry_time:
            self.packaging_expiry_time = to_naive_utc(self.packaging_expiry_time)
        if self.expiry_time <= self.prepared_at:
            raise ValueError("Expiry time must be strictly later than preparation time.")
        return self

class FoodBatchUpdate(BaseModel):
    food_name: Optional[str] = Field(None, min_length=2, max_length=255)
    food_description: Optional[str] = None
    food_category: Optional[str] = Field(None, min_length=2, max_length=100)
    quantity: Optional[float] = Field(None, gt=0)
    unit: Optional[str] = Field(None, min_length=1, max_length=50)
    prepared_at: Optional[datetime] = None
    expiry_time: Optional[datetime] = None
    packaging_expiry_time: Optional[datetime] = None
    storage_condition: Optional[str] = None
    storage_temperature: Optional[float] = None
    pickup_address: Optional[str] = Field(None, min_length=3)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    image_url: Optional[str] = None

    @model_validator(mode="after")
    def validate_expiry_update(self):
        if self.prepared_at:
            self.prepared_at = to_naive_utc(self.prepared_at)
        if self.expiry_time:
            self.expiry_time = to_naive_utc(self.expiry_time)
        if self.packaging_expiry_time:
            self.packaging_expiry_time = to_naive_utc(self.packaging_expiry_time)
        if self.prepared_at and self.expiry_time and self.expiry_time <= self.prepared_at:
            raise ValueError("Expiry time must be strictly later than preparation time.")
        return self

class FoodBatchResponse(BaseModel):
    batch_id: int
    donor_id: int
    donor_name: Optional[str] = None
    donor_phone: Optional[str] = None
    food_name: str
    food_description: Optional[str] = None
    food_category: str
    quantity: float
    donated_quantity: float
    allocated_quantity: float = 0.0
    remaining_quantity: float
    unit: str
    prepared_at: datetime
    user_expiry_time: Optional[datetime] = None
    effective_expiry_time: Optional[datetime] = None
    expiry_time: datetime
    packaging_expiry_time: Optional[datetime] = None
    storage_condition: str = "ambient"
    storage_temperature: Optional[float] = None
    expiry_validation_status: str = "verified"
    expiry_rule_applied: Optional[str] = None
    expiry_adjustment_reason: Optional[str] = None
    image_url: Optional[str] = None
    food_status: str
    pickup_address: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    remaining_hours: Optional[float] = None
    is_close_to_expiry: bool = False
    urgency_level: Optional[str] = "safe"
    max_holding_hours: Optional[float] = None
    approved_maximum_expiry: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

    @field_serializer(
        "prepared_at",
        "user_expiry_time",
        "effective_expiry_time",
        "expiry_time",
        "packaging_expiry_time",
        "created_at",
        "updated_at",
        "approved_maximum_expiry",
        when_used="json",
    )
    def serialize_datetime(self, dt: Optional[datetime]) -> Optional[str]:
        return format_utc_iso(dt)

class FoodBatchDetailResponse(FoodBatchResponse):
    requests: List[Dict[str, Any]] = []
