from datetime import datetime
from typing import Optional, Literal, Dict, Any
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)
    role: Literal["donor", "ngo", "volunteer"]
    phone: str = Field(..., min_length=5, max_length=50)
    address: Optional[str] = None
    organization_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: int
    name: str
    email: str

class UserProfileResponse(BaseModel):
    user_id: int
    name: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    profile: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)

class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    organization_name: Optional[str] = None
    availability_status: Optional[Literal["available", "busy", "offline"]] = None
