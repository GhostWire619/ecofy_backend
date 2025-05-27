from sqlalchemy import Column, String, Float, JSON, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.database import Base

class MarketPrice(Base):
    __tablename__ = "market_prices"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    crop_id = Column(String, ForeignKey("crops.id", ondelete="CASCADE"), nullable=False)
    current_price = Column(Float, nullable=False)
    price_trend = Column(JSON, nullable=False)  # Stores price points over time
    percent_change = Column(Float, nullable=False)
    recommendation = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationship
    crop = relationship("Crop", backref="market_prices") 