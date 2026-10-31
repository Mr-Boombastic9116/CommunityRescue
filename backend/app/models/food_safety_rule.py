from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Numeric, Boolean, DateTime, Index
from app.database.session import Base

class FoodSafetyRule(Base):
    __tablename__ = "food_safety_rules"

    rule_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    food_category = Column(String(100), nullable=False)
    product_type = Column(String(150), nullable=False)
    storage_condition = Column(String(50), nullable=False)  # 'ambient', 'refrigerated', 'frozen', 'hot_holding'
    temperature_min_c = Column(Numeric(5, 2), nullable=True)
    temperature_max_c = Column(Numeric(5, 2), nullable=True)
    max_holding_hours = Column(Numeric(8, 2), nullable=False)  # Maximum allowable hours after preparation
    source_name = Column(String(150), nullable=False)  # e.g., 'FSSAI Surplus Food Guidelines'
    source_url = Column(Text, nullable=True)
    rule_version = Column(String(50), default="FSSAI-2023-V1", nullable=False)
    requires_manual_verification = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("idx_rule_category_storage", "food_category", "storage_condition"),
        Index("idx_rule_product_type", "product_type"),
    )

