import uuid
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.message import Message
from app.repositories.base import BaseRepository


class MessageRepository(BaseRepository[Message]):
    """
    Repository class handling message storage and retrieval within conversations.
    """
    def __init__(self, session: AsyncSession):
        super().__init__(Message, session)

    async def get_by_conversation(self, conversation_id: uuid.UUID) -> List[Message]:
        """Gets all messages in a specific conversation sorted chronologically."""
        stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_recent_context(self, conversation_id: uuid.UUID, limit: int = 10) -> List[Message]:
        """Gets the most recent message logs to feed as context window to the LLM."""
        stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        # Reverse to maintain original chronological order
        return list(reversed(result.scalars().all()))
