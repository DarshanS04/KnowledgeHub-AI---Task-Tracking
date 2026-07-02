import uuid
from sqlalchemy import BigInteger, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional, TYPE_CHECKING
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.document_chunk import DocumentChunk
    from app.models.processing_job import ProcessingJob
    from app.models.upload_log import UploadLog


class Document(BaseModel):
    """
    Document model storing the reference to physical/ingested documents,
    processing status, and raw user metadata.
    """
    __tablename__ = "documents"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # "pdf", "docx", "txt", "md", "github", "youtube", "notes"
    source_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    source_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    file_size: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    total_chunks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # "pending", "processing", "completed", "failed"
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False, index=True)
    meta_info: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="documents")
    chunks: Mapped[List["DocumentChunk"]] = relationship(
        "DocumentChunk", back_populates="document", cascade="all, delete-orphan"
    )
    processing_jobs: Mapped[List["ProcessingJob"]] = relationship(
        "ProcessingJob", back_populates="document", cascade="all, delete-orphan"
    )
    upload_logs: Mapped[List["UploadLog"]] = relationship(
        "UploadLog", back_populates="document", cascade="all, delete-orphan"
    )
