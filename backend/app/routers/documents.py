import uuid
from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.common import DataResponse, PaginatedResponse, PaginatedMetadata
from app.schemas.document import DocumentResponse, NoteCreateRequest
from app.services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post(
    "/upload",
    response_model=DataResponse[DocumentResponse],
    status_code=status.HTTP_202_ACCEPTED,
)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Uploads a document file (PDF, DOCX, TXT, MD), saves it locally,
    and schedules async indexing in background tasks.
    """
    doc_service = DocumentService(db)
    document = await doc_service.upload_document(current_user.id, file, background_tasks)
    return DataResponse(data=DocumentResponse.model_validate(document))


@router.post(
    "/notes",
    response_model=DataResponse[DocumentResponse],
    status_code=status.HTTP_202_ACCEPTED,
)
async def create_note(
    background_tasks: BackgroundTasks,
    payload: NoteCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Saves a manual note as a markdown file, and schedules async vector indexing.
    """
    doc_service = DocumentService(db)
    document = await doc_service.create_note_document(current_user.id, payload, background_tasks)
    return DataResponse(data=DocumentResponse.model_validate(document))


@router.get(
    "",
    response_model=PaginatedResponse[DocumentResponse],
    status_code=status.HTTP_200_OK,
)
async def list_documents(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Fetches a paginated list of documents uploaded by the current user."""
    doc_service = DocumentService(db)
    documents, total = await doc_service.get_user_documents(current_user.id, page, size)
    
    pages = (total + size - 1) // size
    return PaginatedResponse(
        data=[DocumentResponse.model_validate(doc) for doc in documents],
        meta=PaginatedMetadata(
            total=total,
            page=page,
            size=size,
            pages=pages
        )
    )


@router.delete(
    "/{document_id}",
    response_model=DataResponse[str],
    status_code=status.HTTP_200_OK,
)
async def delete_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Removes document records and cleans up vector database entries."""
    doc_service = DocumentService(db)
    await doc_service.delete_document(current_user.id, document_id)
    return DataResponse(data="Document deleted successfully.")
