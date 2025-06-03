from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Coordinates(BaseModel):
    lat: str
    lng: str

class SoilParameters(BaseModel):
    moisture: str
    organic_carbon: str
    texture: str
    ph: str
    ec: Optional[str] = None
    salinity: Optional[str] = None
    water_holding: Optional[str] = None
    organic_matter: Optional[str] = None
    npk: Optional[str] = None

class CropHistory(BaseModel):
    crop: str
    season: str
    yield_amount: str
    
class FarmBase(BaseModel):
    name: str
    location: str
    size: str
    topography: Optional[str] = None
    coordinates: Coordinates
    soil_params: Optional[SoilParameters] = None
   

class FarmCreate(BaseModel):
    name: str
    location: str
    size: str
    topography: Optional[str] = None
    coordinates: Coordinates
 

class FarmResponse(FarmBase):
    id: str
    user_id: str
    image: Optional[str] = None
    crop_history: List[CropHistory] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True 