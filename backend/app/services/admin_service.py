import uuid
from typing import List, Dict, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.upload_log import UploadLog
from app.models.processing_job import ProcessingJob
from app.repositories.user_repository import UserRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.upload_log_repository import UploadLogRepository
from app.repositories.processing_job_repository import ProcessingJobRepository
from app.schemas.admin import SystemStatsResponse, UploadLogSchema, ProcessingJobSchema
from app.schemas.user import UserResponse


class AdminService:
    """
    Service class managing system statistics, audit logs, and user admin actions.
    """
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)
        self.doc_repo = DocumentRepository(session)
        self.log_repo = UploadLogRepository(session)
        self.job_repo = ProcessingJobRepository(session)

    async def get_system_stats(self) -> SystemStatsResponse:
        """Counts aggregates for system statistics overview."""
        users_count = await self.session.execute(select(func.count(User.id)))
        docs_count = await self.session.execute(select(func.count(Document.id)))
        chunks_count = await self.session.execute(select(func.count(DocumentChunk.id)))
        convs_count = await self.session.execute(select(func.count(Conversation.id)))
        msgs_count = await self.session.execute(select(func.count(Message.id)))

        return SystemStatsResponse(
            total_users=users_count.scalar_one(),
            total_documents=docs_count.scalar_one(),
            total_chunks=chunks_count.scalar_one(),
            total_conversations=convs_count.scalar_one(),
            total_messages=msgs_count.scalar_one(),
        )

    async def get_all_users(self, skip: int = 0, limit: int = 100) -> List[UserResponse]:
        """Lists registered accounts in the system."""
        users = await self.user_repo.get_multi(skip=skip, limit=limit)
        return [UserResponse.model_validate(u) for u in users]

    async def delete_user(self, user_id: uuid.UUID) -> None:
        """Deletes user from DB. Cascades their documents, logs, and sessions."""
        await self.user_repo.remove(user_id)
        await self.session.commit()

    async def get_upload_logs(self, skip: int = 0, limit: int = 100) -> List[UploadLogSchema]:
        """Lists upload log audits."""
        stmt = select(UploadLog).order_by(UploadLog.created_at.desc()).offset(skip).limit(limit)
        res = await self.session.execute(stmt)
        return [UploadLogSchema.model_validate(l) for l in res.scalars().all()]

    async def get_processing_queue(self, skip: int = 0, limit: int = 100) -> List[ProcessingJobSchema]:
        """Lists processing queue jobs."""
        stmt = select(ProcessingJob).order_by(ProcessingJob.created_at.desc()).offset(skip).limit(limit)
        res = await self.session.execute(stmt)
        return [ProcessingJobSchema.model_validate(j) for j in res.scalars().all()]
