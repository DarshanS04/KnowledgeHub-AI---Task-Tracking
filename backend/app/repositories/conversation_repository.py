import uuid
from typing import List, Tuple
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.conversation import Conversation
from app.repositories.base import BaseRepository


class ConversationRepository(BaseRepository[Conversation]):
    """
    Repository class handling CRUD and query operations for Conversation models.
    """
    def __init__(self, session: AsyncSession):
        super().__init__(Conversation, session)

    async def get_by_user(
        self, user_id: uuid.UUID, skip: int = 0, limit: int = 20
    ) -> Tuple[List[Conversation], int]:
        """
        Gets a page of conversation history for a given user ID,
        returning a tuple (conversations, total_count).
        """
        count_stmt = select(func.count()).select_from(Conversation).where(Conversation.user_id == user_id)
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar_one()

        stmt = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all()), total
