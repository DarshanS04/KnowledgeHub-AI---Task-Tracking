import uuid
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, TYPE_CHECKING
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.document import Document


class UploadLog(BaseModel):
    """
    UploadLog model tracking user ingestion actions, outcomes, and audit information.
    """
    __tablename__ = "upload_logs"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    document_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("documents.id", ondelete="SET NULL"), nullable=True, index=True
    )
    
    action: Mapped[str] = mapped_column(String(50), nullable=False) # e.g. "upload", "github_clone", "youtube_fetch"
    status: Mapped[str] = mapped_column(String(20), nullable=False) # "success" or "failed"
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="upload_logs")
    document: Mapped[Optional["Document"]] = relationship("Document", back_populates="upload_logs")
