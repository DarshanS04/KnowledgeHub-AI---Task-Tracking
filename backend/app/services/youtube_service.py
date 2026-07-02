import re
import tempfile
import logging
import uuid
from typing import Optional
from youtube_transcript_api import YouTubeTranscriptApi
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.document import Document
from app.repositories.document_repository import DocumentRepository
from app.repositories.upload_log_repository import UploadLogRepository
from app.services.processing_service import ProcessingService

logger = logging.getLogger(__name__)


class YoutubeService:
    """
    Service class managing fetching and parsing YouTube transcripts.
    """
    def __init__(self, session: AsyncSession):
        self.session = session
        self.doc_repo = DocumentRepository(session)
        self.log_repo = UploadLogRepository(session)

    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        """Extracts the 11-character video ID from a YouTube link."""
        pattern = r'(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})'
        match = re.search(pattern, url)
        return match.group(1) if match else None

    async def ingest_transcript(
        self,
        user_id: uuid.UUID,
        video_url: str,
        background_tasks
    ) -> Document:
        """
        Fetches the transcript for a YouTube video and schedules ingestion.
        """
        video_id = self.extract_video_id(video_url)
        if not video_id:
            raise ValueError("Invalid YouTube URL. Could not extract Video ID.")

        document = await self.doc_repo.create({
            "user_id": user_id,
            "filename": f"youtube-{video_id}",
            "original_filename": f"YouTube Video: {video_id}",
            "source_type": "youtube",
            "source_url": video_url,
            "status": "processing",
            "meta_info": {"video_id": video_id, "video_url": video_url}
        })

        await self.log_repo.create({
            "user_id": user_id,
            "document_id": document.id,
            "action": "youtube_fetch",
            "status": "success",
        })
        await self.session.commit()

        # Run transcript download in background
        background_tasks.add_task(
            self._download_and_process_transcript,
            document.id,
            video_id
        )

        return document

    async def _download_and_process_transcript(self, document_id: uuid.UUID, video_id: str) -> None:
        """Downloads the transcript text, writes it locally, and launches standard parsing."""
        try:
            # Fetch transcript list
            # We try English ('en') first, then fall back to auto-generated or other languages
            try:
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
            except Exception:
                # Fall back to any language available
                transcript_dict = YouTubeTranscriptApi.list_transcripts(video_id)
                transcript_list = transcript_dict.find_transcript(['en', 'es', 'fr', 'de']).fetch()

            # Format the transcript text
            full_transcript_text = ""
            for segment in transcript_list:
                start_sec = int(segment['start'])
                # Convert seconds to MM:SS format
                min_part = start_sec // 60
                sec_part = start_sec % 60
                timestamp = f"[{min_part:02d}:{sec_part:02d}]"
                full_transcript_text += f"{timestamp} {segment['text']}\n"

            if not full_transcript_text.strip():
                raise ValueError("YouTube transcript is empty.")

            # Save formatted text into a temp file for the pipeline
            temp_file_path = tempfile.mktemp(suffix=".txt")
            with open(temp_file_path, "w", encoding="utf-8") as f:
                f.write(full_transcript_text)

            processing_service = ProcessingService(self.session)
            await processing_service.process_document(document_id, temp_file_path)

        except Exception as e:
            logger.exception(f"Failed to process YouTube transcript for document {document_id}:")
            doc_service = ProcessingService(self.session)
            document = await self.doc_repo.get(document_id)
            if document:
                await self.doc_repo.update(document, {"status": "failed"})
                await doc_service.job_repo.create({
                    "document_id": document_id,
                    "job_type": "all",
                    "status": "failed",
                    "error_message": f"YouTube fetch failed: {str(e)}"
                })
                await self.session.commit()
