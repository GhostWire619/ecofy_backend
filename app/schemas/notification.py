from pydantic import BaseModel
from enum import Enum
from datetime import datetime

class NotificationType(str, Enum):
    SYSTEM = "system"
    WEATHER = "weather"
    MARKET = "market"
    ORDER = "order"
    PEST = "pest"
    OTHER = "other"

class NotificationResponse(BaseModel):
    id: str
    user_id: str
    title: str
    message: str
    type: NotificationType
    is_read: bool = False
    created_at: datetime

    class Config:
        orm_mode = True 