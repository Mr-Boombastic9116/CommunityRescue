from sqlalchemy import Column, Integer, String, Text, Numeric, ForeignKey
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

    user = relationship("User", back_populates="ngo")
    pickup_requests = relationship("PickupRequest", back_populates="ngo", cascade="all, delete-orphan")

