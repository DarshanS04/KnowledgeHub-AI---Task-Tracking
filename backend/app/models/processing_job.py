import uuid
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, TYPE_CHECKING
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.document import Document


class ProcessingJob(BaseModel):
    """
    ProcessingJob model storing metadata about ongoing asynchronous pipelines 
    for document parsing, splitting, embedding, and vector insertion.
    """
    __tablename__ = "processing_jobs"

    document_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    # "extract", "chunk", "embed", "index", "all"
    job_type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # "queued", "running", "completed", "failed"
    status: Mapped[str] = mapped_column(String(20), default="queued", nullable=False, index=True)
    progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False) # 0 to 100
    
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    document: Mapped["Document"] = relationship("Document", back_populates="processing_jobs")
