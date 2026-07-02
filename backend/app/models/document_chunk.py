import uuid
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, TYPE_CHECKING
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.document import Document


class DocumentChunk(BaseModel):
    """
    DocumentChunk model holding split text parts of a document and mapping 
    to the vector point ID in Qdrant.
    """
    __tablename__ = "document_chunks"

    document_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    chunk_number: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    page_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    qdrant_point_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    meta_info: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    # Relationships
    document: Mapped["Document"] = relationship("Document", back_populates="chunks")
