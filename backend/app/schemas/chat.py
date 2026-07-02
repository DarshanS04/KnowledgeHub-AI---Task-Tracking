import uuid
from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel


class MessageBase(BaseModel):
    role: str
    content: str


class MessageResponse(MessageBase):
    id: uuid.UUID
    conversation_id: uuid.UUID
    citations: Optional[List[Dict[str, Any]]] = None
    token_count: Optional[int] = None
    response_time: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationBase(BaseModel):
    title: str


class ConversationCreate(ConversationBase):
    pass


class ConversationResponse(ConversationBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    conversation_id: Optional[uuid.UUID] = None
    message: str
    stream: bool = True
