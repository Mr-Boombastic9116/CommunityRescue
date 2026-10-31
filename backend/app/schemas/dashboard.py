from typing import Dict, Any, List
from pydantic import BaseModel

class DonorDashboardStats(BaseModel):
    total_donations: int
    available_donations: int
    in_progress_donations: int
    completed_donations: int
    expired_donations: int
    total_quantity_donated: float
    recent_activities: List[Dict[str, Any]] = []

class NGODashboardStats(BaseModel):
    total_requests: int
    pending_requests: int
    assigned_requests: int
    collected_requests: int
    completed_requests: int
    cancelled_requests: int
    total_quantity_received: float
    recent_activities: List[Dict[str, Any]] = []

class VolunteerDashboardStats(BaseModel):
    total_claimed: int
    assigned_tasks: int
    collected_tasks: int
    completed_tasks: int
    availability_status: str
    recent_activities: List[Dict[str, Any]] = []

