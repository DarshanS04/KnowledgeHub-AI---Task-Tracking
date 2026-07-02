import os
import uuid
import logging
from typing import List, Tuple, Dict, Any
from fastapi import UploadFile, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.exceptions import AppException, NotFoundException
from app.models.document import Document
from app.repositories.document_repository import DocumentRepository
from app.repositories.upload_log_repository import UploadLogRepository
from app.services.processing_service import ProcessingService
from app.services.vector_service import VectorService

logger = logging.getLogger(__name__)


class DocumentService:
    """
    Service class managing document creation, storage, uploads, paginations, and deletions.
    """
    def __init__(self, session: AsyncSession):
        self.session = session
        self.doc_repo = DocumentRepository(session)
        self.log_repo = UploadLogRepository(session)
        self.vector_service = VectorService()

    async def upload_document(
        self,
        user_id: uuid.UUID,
        file: UploadFile,
        background_tasks: BackgroundTasks
    ) -> Document:
        """
        Saves a local file, registers a Document record, and schedules async ingestion.
        """
        filename = file.filename
        if not filename:
            raise AppException(status_code=400, message="Filename cannot be empty.")

        ext = os.path.splitext(filename.lower())[1]
        allowed_extensions = {".pdf", ".docx", ".doc", ".txt", ".md"}
        if ext not in allowed_extensions:
            raise AppException(status_code=400, message=f"Unsupported file type: {ext}")

        # Check file size (Read chunks to prevent loading huge files in memory)
        content_length = 0
        temp_file_path = os.path.join(settings.UPLOAD_DIR, f"{uuid.uuid4()}{ext}")
        
        # Ensure uploads folder exists
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

        try:
            with open(temp_file_path, "wb") as f:
                while chunk := await file.read(1024 * 1024): # Read in 1MB chunks
                    content_length += len(chunk)
                    if content_length > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
                        raise AppException(
                            status_code=413,
                            message=f"File exceeds maximum upload size of {settings.MAX_UPLOAD_SIZE_MB}MB."
                        )
                    f.write(chunk)
        except Exception:
            # Clean up temp file on failure
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            raise

        # Save record to Database
        source_type = ext[1:] # e.g. "pdf", "docx", "txt", "md"
        document = await self.doc_repo.create({
            "user_id": user_id,
            "filename": os.path.basename(temp_file_path),
            "original_filename": filename,
            "source_type": source_type,
            "file_size": content_length,
            "status": "processing",
        })

        # Save upload log entry
        await self.log_repo.create({
            "user_id": user_id,
            "document_id": document.id,
            "action": "upload",
            "status": "success",
        })
        await self.session.commit()

        # Add async background process job
        processing_service = ProcessingService(self.session)
        background_tasks.add_task(
            processing_service.process_document,
            document.id,
            temp_file_path
        )

        return document

    async def create_note_document(
        self,
        user_id: uuid.UUID,
        note_in: Any, # Avoid circular import of schemas if needed, or import directly
        background_tasks: BackgroundTasks
    ) -> Document:
        """
        Saves a rich text note as a Markdown file, registers a Document record,
        and schedules async vector indexing.
        """
        title = note_in.title
        content = note_in.content

        # Create note file in uploads folder
        note_id = uuid.uuid4()
        temp_file_path = os.path.join(settings.UPLOAD_DIR, f"note-{note_id}.md")
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

        try:
            with open(temp_file_path, "w", encoding="utf-8") as f:
                f.write(f"# {title}\n\n{content}")
        except Exception as e:
            logger.error(f"Failed to write note to disk: {e}")
            raise RuntimeError("Could not save manual note.")

        file_size = len(title) + len(content) + 5 # approximate character size

        # Save record to Database
        document = await self.doc_repo.create({
            "user_id": user_id,
            "filename": os.path.basename(temp_file_path),
            "original_filename": f"Note: {title}",
            "source_type": "notes",
            "file_size": file_size,
            "status": "processing",
        })

        # Save upload log entry
        await self.log_repo.create({
            "user_id": user_id,
            "document_id": document.id,
            "action": "upload",
            "status": "success",
        })
        await self.session.commit()

        # Add async background process job
        processing_service = ProcessingService(self.session)
        background_tasks.add_task(
            processing_service.process_document,
            document.id,
            temp_file_path
        )

        return document


    async def get_user_documents(
        self,
        user_id: uuid.UUID,
        page: int = 1,
        size: int = 10
    ) -> Tuple[List[Document], int]:
        """Fetches a paginated list of documents uploaded by the user."""
        skip = (page - 1) * size
        return await self.doc_repo.get_by_user(user_id, skip, size)

    async def delete_document(self, user_id: uuid.UUID, document_id: uuid.UUID) -> None:
        """
        Deletes a document from the database and removes all its vector points from Qdrant.
        """
        document = await self.doc_repo.get(document_id)
        if not document:
            raise NotFoundException(message="Document not found.")

        # Ensure ownership
        if document.user_id != user_id:
            raise AppException(status_code=403, message="Access forbidden to this document.")

        # 1. Delete vectors from Qdrant first
        await self.vector_service.delete_by_document(document_id)

        # 2. Delete relational records from database (Cascades chunks/jobs automatically)
        await self.doc_repo.remove(document_id)
        await self.session.commit()
