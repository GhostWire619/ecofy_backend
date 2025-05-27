from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class PricePoint(BaseModel):
    date: datetime
    price: float
    
class MarketData(BaseModel):
    crop_id: str
    crop_name: str
    current_price: float
    price_trend: List[PricePoint]
    percent_change: float
    recommendation: Optional[str] = None

class MarketDataResponse(BaseModel):
    data: List[MarketData] 