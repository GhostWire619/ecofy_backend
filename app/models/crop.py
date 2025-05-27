from sqlalchemy import Column, String, JSON, DateTime
from sqlalchemy.sql import func
import uuid

from app.database import Base

class Crop(Base):
    __tablename__ = "crops"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, index=True)
    description = Column(String, nullable=False)
    optimal_planting_time = Column(String, nullable=False)
    climate_requirements = Column(JSON, nullable=False)  # Stores climate requirements
    soil_requirements = Column(JSON, nullable=False)  # Stores soil requirements
    risks = Column(JSON, nullable=False)  # Stores risks
    image = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False) 