from fastapi import APIRouter, Depends, BackgroundTasks, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.common import DataResponse
from app.schemas.document import DocumentResponse, YoutubeImportRequest
from app.services.youtube_service import YoutubeService

router = APIRouter(prefix="/youtube", tags=["YouTube Integration"])


@router.post(
    "",
    response_model=DataResponse[DocumentResponse],
    status_code=status.HTTP_202_ACCEPTED,
)
async def import_youtube(
    background_tasks: BackgroundTasks,
    payload: YoutubeImportRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Downloads transcript for a YouTube video URL and indexes it asynchronously.
    """
    youtube_service = YoutubeService(db)
    document = await youtube_service.ingest_transcript(
        current_user.id,
        payload.video_url,
        background_tasks
    )
    return DataResponse(data=DocumentResponse.model_validate(document))
