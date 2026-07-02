from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel


class SearchRequest(BaseModel):
    query: str
    source_type: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = 5


class SearchResult(BaseModel):
    filename: str
    page: Optional[int] = None
    chunk_number: int
    similarity_score: float
    preview_snippet: str
    document_id: str
