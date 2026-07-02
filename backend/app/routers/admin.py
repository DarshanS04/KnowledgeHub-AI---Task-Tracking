import uuid
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.dependencies import get_current_admin
from app.models.user import User
from app.schemas.common import DataResponse
from app.schemas.admin import SystemStatsResponse, UploadLogSchema, ProcessingJobSchema
from app.schemas.user import UserResponse
from app.services.admin_service import AdminService

router = APIRouter(prefix="/admin", tags=["Admin Operations"])


@router.get(
    "/stats",
    response_model=DataResponse[SystemStatsResponse],
    status_code=status.HTTP_200_OK,
)
async def get_system_stats(
    admin_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves system statistical metrics aggregated across tables."""
    admin_service = AdminService(db)
    stats = await admin_service.get_system_stats()
    return DataResponse(data=stats)


@router.get(
    "/users",
    response_model=DataResponse[list[UserResponse]],
    status_code=status.HTTP_200_OK,
)
async def list_users(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=100, ge=1, le=100),
    admin_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Lists registered accounts in the system."""
    admin_service = AdminService(db)
    skip = (page - 1) * size
    users = await admin_service.get_all_users(skip, size)
    return DataResponse(data=users)


@router.delete(
    "/users/{user_id}",
    response_model=DataResponse[str],
    status_code=status.HTTP_200_OK,
)
async def delete_user(
    user_id: uuid.UUID,
    admin_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Deletes user registration, cascading document/chat logs."""
    admin_service = AdminService(db)
    await admin_service.delete_user(user_id)
    return DataResponse(data="User deleted successfully.")


@router.get(
    "/upload-logs",
    response_model=DataResponse[list[UploadLogSchema]],
    status_code=status.HTTP_200_OK,
)
async def list_upload_logs(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=100, ge=1, le=100),
    admin_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Lists recent document ingestion attempt logs."""
    admin_service = AdminService(db)
    skip = (page - 1) * size
    logs = await admin_service.get_upload_logs(skip, size)
    return DataResponse(data=logs)


@router.get(
    "/processing-queue",
    response_model=DataResponse[list[ProcessingJobSchema]],
    status_code=status.HTTP_200_OK,
)
async def list_processing_queue(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=100, ge=1, le=100),
    admin_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Lists recent document vector processing queue jobs."""
    admin_service = AdminService(db)
    skip = (page - 1) * size
    jobs = await admin_service.get_processing_queue(skip, size)
    return DataResponse(data=jobs)
