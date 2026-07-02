from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.common import DataResponse
from app.schemas.search import SearchRequest, SearchResult
from app.services.search_service import SearchService

router = APIRouter(prefix="/search", tags=["Search"])


@router.post(
    "",
    response_model=DataResponse[list[SearchResult]],
    status_code=status.HTTP_200_OK,
)
async def search(
    payload: SearchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Executes a semantic similarity lookup in the Qdrant vector space
    using query text embedding.
    """
    search_service = SearchService()
    results = await search_service.execute_search(
        query=payload.query,
        user_id=current_user.id,
        source_type=payload.source_type,
        limit=payload.limit
    )
    return DataResponse(data=results)

