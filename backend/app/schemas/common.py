from typing import Any, Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class APIError(BaseModel):
    code: int
    message: str
    details: Optional[Any] = None


class BaseResponse(BaseModel):
    success: bool = True
    error: Optional[APIError] = None


class DataResponse(BaseResponse, Generic[T]):
    data: T


class PaginatedMetadata(BaseModel):
    total: int
    page: int
    size: int
    pages: int


class PaginatedResponse(BaseResponse, Generic[T]):
    data: List[T]
    meta: PaginatedMetadata


class PaginationQuery(BaseModel):
    page: int = Field(default=1, ge=1, description="Page number starting from 1")
    size: int = Field(default=10, ge=1, le=100, description="Number of items per page")
