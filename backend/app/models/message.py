import uuid
from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, TYPE_CHECKING
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.conversation import Conversation


class Message(BaseModel):
    """
    Message model holding user inputs or assistant responses in a chat session.
    """
    __tablename__ = "messages"

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    # "user" or "assistant"
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # List of citations: [{filename, page_number, chunk_number, snippet, similarity_score}]
    citations: Mapped[Optional[dict]] = mapped_column(JSONB, default=None, nullable=True)
    token_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    response_time: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Relationships
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="messages")
