from datetime import datetime, timezone
from typing import Optional

def to_naive_utc(dt: Optional[datetime]) -> Optional[datetime]:
    if dt is None:
        return None
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt

def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)

