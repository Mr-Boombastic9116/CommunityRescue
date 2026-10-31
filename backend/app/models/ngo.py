from sqlalchemy import Column, Integer, String, Text, Numeric, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database.session import Base

class NGOPartner(Base):
    __tablename__ = "ngo_partners"

    ngo_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    ngo_name = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=False)
    address = Column(Text, nullable=False)
    latitude = Column(Numeric(10, 8), nullable=True)
    longitude = Column(Numeric(11, 8), nullable=True)

    # Feature D: Smart Matching Parameters
    preferred_categories = Column(String(255), nullable=True, default="Cooked Meals, Bakery & Bread, Raw Food/Produce")
    capacity_servings = Column(Integer, nullable=True, default=100)
    operating_hours = Column(String(100), nullable=True, default="09:00 - 21:00")
    is_active = Column(Boolean, default=True, nullable=False)

    user = relationship("User", back_populates="ngo")
    pickup_requests = relationship("PickupRequest", back_populates="ngo", cascade="all, delete-orphan")

