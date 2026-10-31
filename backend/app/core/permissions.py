from typing import List, Callable, Dict, Set
from fastapi import Depends, HTTPException, status
from app.api.deps import get_current_user
from app.models.user import User

ROLE_DONOR = "donor"
ROLE_NGO = "ngo"
ROLE_VOLUNTEER = "volunteer"

ALL_ROLES = [ROLE_DONOR, ROLE_NGO, ROLE_VOLUNTEER]

# Centralized Role Permissions Catalog
ROLE_PERMISSIONS: Dict[str, Set[str]] = {
    ROLE_DONOR: {
        "donations:create",
        "donations:edit_own",
        "donations:view_own",
        "donations:cancel_own",
        "donations:view_allocations",
        "donations:view_expiry_alerts",
        "ai:recognize_image",
        "ai:generate_description",
        "ai:categorize_food",
        "dashboard:donor_stats",
    },
    ROLE_NGO: {
        "donations:browse_marketplace",
        "donations:view_details",
        "requests:create",
        "requests:view_own",
        "requests:cancel_own",
        "requests:view_allocations",
        "requests:track_delivery",
        "ai:smart_match",
        "dashboard:ngo_stats",
    },
    ROLE_VOLUNTEER: {
        "tasks:view_available",
        "tasks:claim",
        "tasks:view_assigned",
        "tasks:update_collection",
        "tasks:update_delivery",
        "tasks:view_history",
        "volunteer:set_availability",
        "ai:prioritize_tasks",
        "dashboard:volunteer_stats",
    },
}

def check_user_permission(user: User, required_permission: str) -> bool:
    user_perms = ROLE_PERMISSIONS.get(user.role, set())
    return required_permission in user_perms

def require_role(allowed_role: str) -> Callable:
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role != allowed_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: operation restricted to '{allowed_role}' role (current role: '{current_user.role}').",
            )
        return current_user
    return role_checker

def require_permission(permission: str) -> Callable:
    def perm_checker(current_user: User = Depends(get_current_user)) -> User:
        if not check_user_permission(current_user, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: role '{current_user.role}' lacks permission '{permission}'.",
            )
        return current_user
    return perm_checker

