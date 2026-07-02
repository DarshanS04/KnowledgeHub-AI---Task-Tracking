from typing import List, Tuple
import uuid
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.upload_log import UploadLog
from app.repositories.base import BaseRepository


class UploadLogRepository(BaseRepository[UploadLog]):
    """
    Repository class handling operations related to audit logging of uploads.
    """
    def __init__(self, session: AsyncSession):
        super().__init__(UploadLog, session)

    async def get_by_user(
        self, user_id: uuid.UUID, skip: int = 0, limit: int = 20
    ) -> Tuple[List[UploadLog], int]:
        """Gets a page of upload logs for a user, returning (logs, total_count)."""
        count_stmt = select(func.count()).select_from(UploadLog).where(UploadLog.user_id == user_id)
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar_one()

        stmt = (
            select(UploadLog)
            .where(UploadLog.user_id == user_id)
            .order_by(UploadLog.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all()), total
