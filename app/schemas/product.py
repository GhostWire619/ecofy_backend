from pydantic import BaseModel
from typing import List, Optional
from enum import Enum
from datetime import datetime

class ProductCategory(str, Enum):
    SEEDS = "seeds"
    FERTILIZER = "fertilizer"
    PESTICIDE = "pesticide"
    EQUIPMENT = "equipment"
    HARVEST = "harvest"
    LIVESTOCK = "livestock"
    OTHER = "other"

class ProductBase(BaseModel):
    name: str
    description: str
    price: float
    quantity: int
    unit: str
    category: ProductCategory
    location: str
    
class ProductCreate(ProductBase):
    images: List[str] = []

class ProductResponse(ProductBase):
    id: str
    seller_id: str
    seller_name: str
    images: List[str] = []
    rating: Optional[float] = None
    created_at: datetime

    class Config:
        orm_mode = True 