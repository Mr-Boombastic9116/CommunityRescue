from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.session import Base

class Volunteer(Base):
    __tablename__ = "volunteers"

    volunteer_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    volunteer_name = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=False)
    availability_status = Column(String(50), default="available", nullable=False)  # 'available', 'busy', 'offline'
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="volunteer")
    pickup_requests = relationship("PickupRequest", back_populates="volunteer")

