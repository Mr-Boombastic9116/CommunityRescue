from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, ForeignKey, CheckConstraint, Index
from sqlalchemy.orm import relationship
from app.database.session import Base

class FoodBatch(Base):
    __tablename__ = "food_batches"

    batch_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    donor_id = Column(Integer, ForeignKey("donors.donor_id", ondelete="CASCADE"), nullable=False, index=True)
    food_name = Column(String(255), nullable=False)
    food_description = Column(Text, nullable=True)
    food_category = Column(String(100), nullable=False)
    quantity = Column(Numeric(10, 2), nullable=False)
    unit = Column(String(50), nullable=False)
    prepared_at = Column(DateTime, nullable=False)
    user_expiry_time = Column(DateTime, nullable=True)
    effective_expiry_time = Column(DateTime, nullable=True)
    expiry_time = Column(DateTime, nullable=False)
    packaging_expiry_time = Column(DateTime, nullable=True)
    storage_condition = Column(String(50), default="ambient", nullable=False)  # 'ambient', 'refrigerated', 'frozen', 'hot_holding'
    storage_temperature = Column(Numeric(5, 2), nullable=True)
    expiry_validation_status = Column(String(50), default="verified", nullable=False)  # 'verified', 'adjusted', 'manual_verification_required'
    expiry_rule_applied = Column(String(255), nullable=True)
    image_url = Column(Text, nullable=True)
    food_status = Column(String(50), default="available", nullable=False)  # 'available', 'partially_reserved', 'reserved', 'assigned', 'collected', 'delivered', 'expired', 'cancelled', 'completed'
    pickup_address = Column(Text, nullable=False)
    latitude = Column(Numeric(10, 8), nullable=True)
    longitude = Column(Numeric(11, 8), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        CheckConstraint("quantity > 0", name="chk_food_quantity_positive"),
        CheckConstraint("expiry_time > prepared_at", name="chk_food_expiry_after_prep"),
        Index("idx_food_status", "food_status"),
        Index("idx_food_expiry", "expiry_time"),
        Index("idx_food_category", "food_category"),
    )

    donor = relationship("Donor", back_populates="food_batches")
    pickup_requests = relationship("PickupRequest", back_populates="food_batch", cascade="all, delete-orphan")

