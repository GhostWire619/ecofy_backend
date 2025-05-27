from pydantic import BaseModel
from typing import List
from enum import Enum
from datetime import datetime

class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class OrderItem(BaseModel):
    product_id: str
    product_name: str
    quantity: int
    unit_price: float
    
class OrderCreate(BaseModel):
    items: List[OrderItem]
    delivery_address: str
    payment_method: str
    
class OrderResponse(BaseModel):
    id: str
    user_id: str
    items: List[OrderItem]
    total_amount: float
    status: OrderStatus
    delivery_address: str
    payment_method: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True 