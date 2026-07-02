import uuid
from datetime import datetime
from typing import Optional, Any, Dict
from pydantic import BaseModel


class DocumentBase(BaseModel):
    filename: str
    source_type: str
    source_url: Optional[str] = None
    file_size: Optional[int] = None
    total_chunks: int = 0
    status: str = "pending"


class DocumentResponse(DocumentBase):
    id: uuid.UUID
    user_id: uuid.UUID
    meta_info: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GithubCloneRequest(BaseModel):
    repo_url: str


class YoutubeImportRequest(BaseModel):
    video_url: str


class NoteCreateRequest(BaseModel):
    title: str
    content: str


