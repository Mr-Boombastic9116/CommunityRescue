from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, field_serializer
from app.utils.dates import format_utc_iso

class NotificationResponse(BaseModel):
    notification_id: int
    user_id: int
    title: str
    message: str
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("created_at", when_used="json")
    def serialize_datetime(self, dt: Optional[datetime]) -> Optional[str]:
        return format_utc_iso(dt)
