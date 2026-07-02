from typing import Any, Dict, Optional
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)


class AppException(Exception):
    """Base exception for all application errors."""
    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        message: str = "An unexpected error occurred.",
        details: Optional[Any] = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.message = message
        self.details = details


class NotFoundException(AppException):
    """Resource not found exception."""
    def __init__(self, message: str = "Resource not found.", details: Optional[Any] = None):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message=message,
            details=details,
        )


class UnauthorizedException(AppException):
    """Unauthorized operations exception."""
    def __init__(self, message: str = "Unauthorized access.", details: Optional[Any] = None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message=message,
            details=details,
        )


class ForbiddenException(AppException):
    """Forbidden operations exception."""
    def __init__(self, message: str = "Operation forbidden.", details: Optional[Any] = None):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            message=message,
            details=details,
        )


class ValidationException(AppException):
    """Validation failure exception."""
    def __init__(self, message: str = "Validation failed.", details: Optional[Any] = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message=message,
            details=details,
        )


class RateLimitException(AppException):
    """Rate limit exceeded exception."""
    def __init__(self, message: str = "Rate limit exceeded.", details: Optional[Any] = None):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            message=message,
            details=details,
        )


def register_exception_handlers(app: FastAPI) -> None:
    """Registers global exception handlers for the FastAPI application."""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        logger.error(
            f"AppException: status_code={exc.status_code} message={exc.message} details={exc.details}"
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": exc.status_code,
                    "message": exc.message,
                    "details": exc.details,
                }
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        # Standardize pydantic validation errors
        errors = []
        for error in exc.errors():
            errors.append({
                "loc": error.get("loc"),
                "msg": error.get("msg"),
                "type": error.get("type"),
            })

        logger.warning(f"RequestValidationError: {errors}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "error": {
                    "code": status.HTTP_400_BAD_REQUEST,
                    "message": "Invalid request parameters.",
                    "details": errors,
                }
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled General Exception occurred:")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": {
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "message": "An unexpected server error occurred.",
                    "details": str(exc) if settings.ENVIRONMENT == "development" else None,
                }
            },
        )
