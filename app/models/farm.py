from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.database import Base

class Farm(Base):
    __tablename__ = "farms"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    size = Column(String, nullable=False)
    topography = Column(String, nullable=True)
    coordinates = Column(JSON, nullable=False)  # Stores lat and lng
    soil_params = Column(JSON, nullable=False)  # Stores soil parameters
    image = Column(String, nullable=True)
    crop_history = Column(JSON, nullable=False, default=list)  # Stores list of crop history
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationship
    user = relationship("User", backref="farms") 