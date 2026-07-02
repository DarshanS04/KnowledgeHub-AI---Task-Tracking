import uuid
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.document_chunk import DocumentChunk
from app.repositories.base import BaseRepository


class DocumentChunkRepository(BaseRepository[DocumentChunk]):
    """
    Repository class handling operations related to DocumentChunk database queries.
    """
    def __init__(self, session: AsyncSession):
        super().__init__(DocumentChunk, session)

    async def get_by_document(self, document_id: uuid.UUID) -> List[DocumentChunk]:
        """Gets all text chunks associated with a specific Document ID."""
        stmt = (
            select(DocumentChunk)
            .where(DocumentChunk.document_id == document_id)
            .order_by(DocumentChunk.chunk_number.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
