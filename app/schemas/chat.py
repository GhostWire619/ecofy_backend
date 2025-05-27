from pydantic import BaseModel
from typing import Optional
from enum import Enum
from datetime import datetime

class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"

class ChatMessage(BaseModel):
    content: str
    type: MessageType = MessageType.TEXT
    file_url: Optional[str] = None
    
class ChatMessageResponse(ChatMessage):
    id: str
    user_id: Optional[str] = None
    is_ai: bool
    created_at: datetime

    class Config:
        orm_mode = True

class ChatSession(BaseModel):
    id: str
    title: str
    created_at: datetime
    last_message: Optional[str] = None
    last_message_time: Optional[datetime] = None 