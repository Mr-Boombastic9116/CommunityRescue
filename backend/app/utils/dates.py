from datetime import datetime, timezone, timedelta
from typing import Optional, Union

# Standard Indian Standard Time (UTC+05:30)
IST = timezone(timedelta(hours=5, minutes=30), name="Asia/Kolkata")

def parse_iso_datetime(val: Union[str, datetime]) -> datetime:
    """
    Parses an ISO datetime string or normalizes a datetime object into an aware UTC datetime.
    Supports formats with 'Z', '+HH:MM', '-HH:MM', or naive strings.
    """
    if isinstance(val, datetime):
        if val.tzinfo is not None:
            return val.astimezone(timezone.utc)
        return val.replace(tzinfo=timezone.utc)
    
    if not isinstance(val, str):
        raise ValueError(f"Cannot parse datetime from type: {type(val)}")
        
    s = val.strip()
    if not s:
        raise ValueError("Datetime string cannot be empty")
        
    if s.endswith("Z") or s.endswith("z"):
        s = s[:-1] + "+00:00"
        
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc)
    # If naive string, treat as UTC
    return dt.replace(tzinfo=timezone.utc)

def to_naive_utc(dt: Optional[Union[datetime, str]]) -> Optional[datetime]:
    """
    Converts a datetime or ISO string to naive UTC datetime (for MySQL/MariaDB storage).
    """
    if dt is None:
        return None
    if isinstance(dt, str):
        dt = parse_iso_datetime(dt)
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt

def to_aware_utc(dt: Optional[Union[datetime, str]]) -> Optional[datetime]:
    """
    Converts a datetime or ISO string to timezone-aware UTC datetime.
    """
    if dt is None:
        return None
    if isinstance(dt, str):
        return parse_iso_datetime(dt)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

def format_utc_iso(dt: Optional[Union[datetime, str]]) -> Optional[str]:
    """
    Formats a datetime as UTC ISO 8601 string ending with 'Z' (e.g., '2026-10-31T08:30:00Z').
    """
    if dt is None:
        return None
    if isinstance(dt, str):
        dt = parse_iso_datetime(dt)
    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

def utc_now() -> datetime:
    """
    Returns the current naive UTC datetime for database operations and comparisons.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)

def utc_now_aware() -> datetime:
    """
    Returns the current timezone-aware UTC datetime.
    """
    return datetime.now(timezone.utc)
