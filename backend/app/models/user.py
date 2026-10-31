from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.database.session import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)  # 'donor', 'ngo', 'volunteer'
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 1-to-1 relationships
    donor = relationship("Donor", back_populates="user", uselist=False, cascade="all, delete-orphan")
    ngo = relationship("NGOPartner", back_populates="user", uselist=False, cascade="all, delete-orphan")
    volunteer = relationship("Volunteer", back_populates="user", uselist=False, cascade="all, delete-orphan")

    # 1-to-many relationships
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    delivery_logs = relationship("DeliveryLog", back_populates="performed_by_user")

