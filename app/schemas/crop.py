from pydantic import BaseModel
from typing import List, Optional

class ClimateRequirements(BaseModel):
    temperature_min: float
    temperature_max: float
    rainfall_min: float
    rainfall_max: float
    humidity_min: float
    humidity_max: float
    growing_season: str

class SoilRequirements(BaseModel):
    soil_type: str
    ph_min: float
    ph_max: float
    nitrogen: str
    phosphorus: str
    potassium: str
    ec: str
    salinity: str
    water_holding: str
    organic_matter: str

class Risk(BaseModel):
    title: str
    description: str
    severity: str

class CropBase(BaseModel):
    name: str
    description: str
    optimal_planting_time: str
    climate_requirements: ClimateRequirements
    soil_requirements: SoilRequirements
    risks: List[Risk]

class CropResponse(CropBase):
    id: str
    image: Optional[str] = None

    class Config:
        orm_mode = True 