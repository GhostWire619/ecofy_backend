from sqlalchemy import Column, String, Float, JSON, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.database import Base
from app.schemas.order import OrderStatus

class Order(Base):
    __tablename__ = "orders"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    items = Column(JSON, nullable=False)  # Stores order items
    total_amount = Column(Float, nullable=False)
    status = Column(String, nullable=False, default=OrderStatus.PENDING.value)
    delivery_address = Column(String, nullable=False)
    payment_method = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationship
    user = relationship("User", backref="orders") 