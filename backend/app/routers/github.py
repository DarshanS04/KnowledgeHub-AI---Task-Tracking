from fastapi import APIRouter, Depends, BackgroundTasks, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.common import DataResponse
from app.schemas.document import DocumentResponse, GithubCloneRequest
from app.services.github_service import GithubService

router = APIRouter(prefix="/github", tags=["GitHub Integration"])


@router.post(
    "",
    response_model=DataResponse[DocumentResponse],
    status_code=status.HTTP_202_ACCEPTED,
)
async def clone_github(
    background_tasks: BackgroundTasks,
    payload: GithubCloneRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Clones a public GitHub repository, extracts code files,
    and indexes them asynchronously.
    """
    github_service = GithubService(db)
    document = await github_service.ingest_repository(
        current_user.id,
        payload.repo_url,
        background_tasks
    )
    return DataResponse(data=DocumentResponse.model_validate(document))
