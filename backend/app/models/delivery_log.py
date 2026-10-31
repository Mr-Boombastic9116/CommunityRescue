from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database.session import Base

class DeliveryLog(Base):
    __tablename__ = "delivery_logs"

    log_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    request_id = Column(Integer, ForeignKey("pickup_requests.request_id", ondelete="CASCADE"), nullable=False, index=True)
    performed_by_user_id = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String(100), nullable=False)
    notes = Column(Text, nullable=True)
    logged_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("idx_log_action", "action"),
        Index("idx_log_time", "logged_at"),
    )

    request = relationship("PickupRequest", back_populates="delivery_logs")
    performed_by_user = relationship("User", back_populates="delivery_logs")

