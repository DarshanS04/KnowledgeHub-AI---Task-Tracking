from typing import List, Tuple, Optional
import uuid
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.document import Document
from app.repositories.base import BaseRepository


class DocumentRepository(BaseRepository[Document]):
    """
    Repository class handling CRUD and query operations for Document models.
    """
    def __init__(self, session: AsyncSession):
        super().__init__(Document, session)

    async def get_by_user(
        self, user_id: uuid.UUID, skip: int = 0, limit: int = 10
    ) -> Tuple[List[Document], int]:
        """
        Gets a page of document records for a given user ID,
        returning a tuple (documents, total_count).
        """
        # Count total
        count_stmt = select(func.count()).select_from(Document).where(Document.user_id == user_id)
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar_one()

        # Query items
        stmt = (
            select(Document)
            .where(Document.user_id == user_id)
            .order_by(Document.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all()), total
