from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database.session import Base

class PickupRequest(Base):
    __tablename__ = "pickup_requests"

    request_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    batch_id = Column(Integer, ForeignKey("food_batches.batch_id", ondelete="CASCADE"), nullable=False, index=True)
    ngo_id = Column(Integer, ForeignKey("ngo_partners.ngo_id", ondelete="CASCADE"), nullable=False, index=True)
    volunteer_id = Column(Integer, ForeignKey("volunteers.volunteer_id", ondelete="SET NULL"), nullable=True, index=True)
    requested_quantity = Column(Numeric(10, 2), nullable=False, default=1.0)
    unit = Column(String(50), nullable=False, default="units")
    request_status = Column(String(50), default="requested", nullable=False)  # 'requested', 'assigned', 'collected', 'delivered', 'cancelled', 'rejected'
    requested_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    assigned_at = Column(DateTime, nullable=True)
    collected_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("idx_request_status", "request_status"),
        Index("idx_req_volunteer", "volunteer_id"),
        Index("idx_req_ngo", "ngo_id"),
        Index("idx_req_batch", "batch_id"),
    )

    food_batch = relationship("FoodBatch", back_populates="pickup_requests")
    ngo = relationship("NGOPartner", back_populates="pickup_requests")
    volunteer = relationship("Volunteer", back_populates="pickup_requests")
    delivery_logs = relationship("DeliveryLog", back_populates="request", cascade="all, delete-orphan")

