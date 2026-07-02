import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.processing_job import ProcessingJob
from app.repositories.base import BaseRepository


class ProcessingJobRepository(BaseRepository[ProcessingJob]):
    """
    Repository class handling queries to monitor processing job progress.
    """
    def __init__(self, session: AsyncSession):
        super().__init__(ProcessingJob, session)

    async def get_by_document(self, document_id: uuid.UUID) -> Optional[ProcessingJob]:
        """Gets the most recent processing job for a specific document."""
        stmt = (
            select(ProcessingJob)
            .where(ProcessingJob.document_id == document_id)
            .order_by(ProcessingJob.created_at.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
