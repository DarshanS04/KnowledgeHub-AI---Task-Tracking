import os
import shutil
import tempfile
import logging
import subprocess
import uuid
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.document import Document
from app.repositories.document_repository import DocumentRepository
from app.repositories.upload_log_repository import UploadLogRepository
from app.services.processing_service import ProcessingService

logger = logging.getLogger(__name__)


class GithubService:
    """
    Service class managing GitHub cloning, filtering, and repository code indexing.
    """
    def __init__(self, session: AsyncSession):
        self.session = session
        self.doc_repo = DocumentRepository(session)
        self.log_repo = UploadLogRepository(session)

    async def ingest_repository(
        self,
        user_id: uuid.UUID,
        repo_url: str,
        background_tasks
    ) -> Document:
        """
        Clones a public Git repository, filters code files, and indexes them.
        """
        # Create a document record for this github repo source
        repo_name = repo_url.rstrip("/").split("/")[-1]
        if repo_name.endswith(".git"):
            repo_name = repo_name[:-4]

        document = await self.doc_repo.create({
            "user_id": user_id,
            "filename": f"github-{repo_name}",
            "original_filename": f"GitHub: {repo_name}",
            "source_type": "github",
            "source_url": repo_url,
            "status": "processing",
            "meta_info": {"repo_url": repo_url}
        })
        
        # Log the action
        await self.log_repo.create({
            "user_id": user_id,
            "document_id": document.id,
            "action": "github_clone",
            "status": "success",
        })
        await self.session.commit()

        # Run cloning and processing in background so API stays non-blocking
        background_tasks.add_task(
            self._clone_and_process_repo,
            document.id,
            repo_url
        )

        return document

    async def _clone_and_process_repo(self, document_id: uuid.UUID, repo_url: str) -> None:
        """Clones and indexes the repository in a temporary workspace."""
        temp_dir = tempfile.mkdtemp()
        logger.info(f"Cloning Git repository {repo_url} into: {temp_dir}")
        
        try:
            # Clone repo using git CLI
            result = subprocess.run(
                ["git", "clone", "--depth", "1", repo_url, temp_dir],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=120 # Timeout after 2 minutes
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"Git clone failed: {result.stderr}")

            # Collect code files
            relevant_files = []
            allowed_extensions = {".py", ".java", ".js", ".ts", ".md", ".json", ".yaml", ".yml"}
            ignored_dirs = {"node_modules", "build", "dist", "target", ".git"}

            for root, dirs, files in os.walk(temp_dir):
                # Prune ignored directories in place
                dirs[:] = [d for d in dirs if d not in ignored_dirs]
                
                for f in files:
                    ext = os.path.splitext(f)[1].lower()
                    if ext in allowed_extensions or f.upper() == "README":
                        relevant_files.append(os.path.join(root, f))

            logger.info(f"Found {len(relevant_files)} relevant files to index in {repo_url}")
            
            # Combine content of all files with markers
            combined_content_list = []
            for filepath in relevant_files:
                relative_path = os.path.relpath(filepath, temp_dir)
                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        file_text = f.read()
                    
                    if file_text.strip():
                        combined_content_list.append(
                            f"=== File: {relative_path} ===\n{file_text}\n"
                        )
                except Exception as fe:
                    logger.warning(f"Failed to read repository file {relative_path}: {fe}")

            if not combined_content_list:
                raise ValueError("No readable code/text files found in repository.")

            # Write combined repository content to a temporary text file for standard ingestion
            combined_file_path = os.path.join(tempfile.gettempdir(), f"github-{document_id}.txt")
            with open(combined_file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(combined_content_list))

            # Trigger standard ingestion pipeline
            processing_service = ProcessingService(self.session)
            await processing_service.process_document(document_id, combined_file_path)

        except Exception as e:
            logger.exception(f"GitHub repository processing failed for document {document_id}:")
            # Update Document state
            doc_service = ProcessingService(self.session)
            document = await self.doc_repo.get(document_id)
            if document:
                await self.doc_repo.update(document, {"status": "failed"})
                # Create fail job status
                job = await doc_service.job_repo.create({
                    "document_id": document_id,
                    "job_type": "all",
                    "status": "failed",
                    "error_message": str(e)[:1000]
                })
                await self.session.commit()
        finally:
            # Clean up temp workspace folder
            try:
                shutil.rmtree(temp_dir)
            except Exception as ce:
                logger.warning(f"Failed to clean up cloned repo temp folder: {ce}")
