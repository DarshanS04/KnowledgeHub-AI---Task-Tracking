import uuid
import logging
import os
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.document import Document
from app.repositories.document_repository import DocumentRepository
from app.repositories.chunk_repository import DocumentChunkRepository
from app.repositories.processing_job_repository import ProcessingJobRepository
from app.utils.file_handlers import FileExtractor
from app.utils.text_processing import clean_text, TokenBasedTextSplitter
from app.services.embedding_service import EmbeddingService
from app.services.vector_service import VectorService

logger = logging.getLogger(__name__)


class ProcessingService:
    """
    Service coordinating text extraction, token chunking, embedding generation,
    and storage across PostgreSQL and Qdrant databases.
    """
    def __init__(self, session: AsyncSession):
        self.session = session
        self.doc_repo = DocumentRepository(session)
        self.chunk_repo = DocumentChunkRepository(session)
        self.job_repo = ProcessingJobRepository(session)
        self.embedding_service = EmbeddingService()
        self.vector_service = VectorService()
        self.splitter = TokenBasedTextSplitter()

    async def process_document(self, document_id: uuid.UUID, filepath: str) -> None:
        """
        Executes the entire document ingestion pipeline asynchronously.
        Designed to be called as a FastAPI BackgroundTask.
        """
        logger.info(f"Starting processing pipeline for document '{document_id}'")
        
        # 1. Create or retrieve ProcessingJob
        job = await self.job_repo.create({
            "document_id": document_id,
            "job_type": "all",
            "status": "running",
            "progress": 5,
            "started_at": datetime.now(timezone.utc),
        })
        await self.session.commit()

        document = await self.doc_repo.get(document_id)
        if not document:
            logger.error(f"Ingestion failed: Document {document_id} not found in DB")
            await self._mark_job_failed(job, "Document not found in DB")
            return

        try:
            # 2. Extract Text
            logger.info(f"Extracting text from: {filepath}")
            await self._update_progress(job, 20, "extracting")
            
            blocks = FileExtractor.extract(filepath, document.original_filename)
            if not blocks:
                raise ValueError("No text could be extracted from the file.")

            # 3. Clean and Chunk Text
            logger.info("Splitting document text into token chunks...")
            await self._update_progress(job, 40, "chunking")
            
            chunk_data_list = [] # List of dicts for DB insertions
            chunk_texts = []
            
            chunk_counter = 1
            for block in blocks:
                text_chunks = self.splitter.split(block.content)
                for txt in text_chunks:
                    chunk_texts.append(txt)
                    chunk_data_list.append({
                        "id": uuid.uuid4(), # Generate UUID for Qdrant point mapping
                        "document_id": document_id,
                        "chunk_number": chunk_counter,
                        "content": txt,
                        "page_number": block.page_number,
                        "meta_info": {
                            "source_type": document.source_type,
                            "filename": document.original_filename,
                            "page_number": block.page_number,
                            "chunk_number": chunk_counter,
                        }
                    })
                    chunk_counter += 1

            if not chunk_texts:
                raise ValueError("Text splitting resulted in zero chunks.")

            # 4. Generate Embeddings
            logger.info(f"Generating embeddings for {len(chunk_texts)} chunks...")
            await self._update_progress(job, 60, "embedding")
            
            embeddings = self.embedding_service.generate_embeddings(chunk_texts)

            # 5. Store in Qdrant Vector DB
            logger.info("Upserting vectors and payload into Qdrant...")
            await self._update_progress(job, 80, "indexing")
            
            qdrant_payloads = []
            for item in chunk_data_list:
                qdrant_payloads.append({
                    "user_id": str(document.user_id),
                    "document_id": str(document.id),
                    "filename": document.original_filename,
                    "page_number": item["page_number"],
                    "chunk_number": item["chunk_number"],
                    "source_type": document.source_type,
                    "uploaded_at": document.created_at.isoformat(),
                    "text": item["content"],
                })

            chunk_ids = [item["id"] for item in chunk_data_list]
            await self.vector_service.upsert_chunks(
                chunk_ids=chunk_ids,
                embeddings=embeddings,
                payloads=qdrant_payloads
            )

            # 6. Save Chunk Records to PostgreSQL
            logger.info("Saving chunks to database...")
            for idx, item in enumerate(chunk_data_list):
                await self.chunk_repo.create({
                    "id": item["id"],
                    "document_id": item["document_id"],
                    "chunk_number": item["chunk_number"],
                    "content": item["content"],
                    "page_number": item["page_number"],
                    "qdrant_point_id": str(item["id"]),
                    "meta_info": item["meta_info"]
                })

            # Update document state to completed
            await self.doc_repo.update(document, {
                "status": "completed",
                "total_chunks": len(chunk_data_list)
            })

            # 7. Update Job Status to Completed
            await self._update_progress(job, 100, "completed")
            logger.info(f"Ingestion pipeline completed successfully for document '{document_id}'")

        except Exception as e:
            logger.exception(f"Ingestion pipeline failed for document '{document_id}':")
            await self.doc_repo.update(document, {"status": "failed"})
            await self._mark_job_failed(job, str(e))
        finally:
            # Clean up the local physical file once ingested (optional, but keeps filesystem clean)
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
            except Exception as ce:
                logger.warning(f"Failed to delete processed file {filepath}: {ce}")
            
            await self.session.commit()

    async def _update_progress(self, job, progress: int, status: str) -> None:
        """Updates progress metrics in the database."""
        job_data = {
            "progress": progress,
            "status": status
        }
        if status == "completed":
            job_data["completed_at"] = datetime.now(timezone.utc)
            
        await self.job_repo.update(job, job_data)
        await self.session.flush()

    async def _mark_job_failed(self, job, error_message: str) -> None:
        """Marks the processing job state as failed with error details."""
        await self.job_repo.update(job, {
            "status": "failed",
            "error_message": error_message[:1000], # Truncate message if too long
            "completed_at": datetime.now(timezone.utc)
        })
        await self.session.flush()
