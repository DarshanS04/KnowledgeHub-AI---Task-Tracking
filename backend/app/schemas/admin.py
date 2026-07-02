from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
import uuid


class SystemStatsResponse(BaseModel):
    total_users: int
    total_documents: int
    total_chunks: int
    total_conversations: int
    total_messages: int


class ProcessingJobSchema(BaseModel):
    id: uuid.UUID
    document_id: uuid.UUID
    job_type: str
    status: str
    progress: int
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UploadLogSchema(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    document_id: Optional[uuid.UUID] = None
    action: str
    status: str
    error_message: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
