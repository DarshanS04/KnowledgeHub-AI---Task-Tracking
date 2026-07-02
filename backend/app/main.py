from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from app.config import settings
from app.core.logging import setup_logging
from app.core.qdrant import init_qdrant
from app.exceptions import register_exception_handlers
from app.middleware import LoggingMiddleware, RequestIDMiddleware, limiter
from app.routers import (
    admin_router,
    auth_router,
    chat_router,
    documents_router,
    github_router,
    health_router,
    search_router,
    youtube_router,
)

# Setup initial logging configuration
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager managing startup and shutdown lifecycle events
    for DB connections, Qdrant client, and other dependencies.
    """
    logger.info("Starting up KnowledgeHub AI Backend...")
    # Initialize Qdrant collection
    await init_qdrant()
    yield
    logger.info("Shutting down KnowledgeHub AI Backend...")


def create_app() -> FastAPI:
    """App factory function to configure and initialize the FastAPI application."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        lifespan=lifespan,
    )

    # Enable slowapi rate limiting state and error handler
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Global middlewares
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(RequestIDMiddleware)

    # Register custom global exceptions
    register_exception_handlers(app)

    # Register API Routers
    app.include_router(auth_router, prefix=settings.API_V1_STR)
    app.include_router(documents_router, prefix=settings.API_V1_STR)
    app.include_router(chat_router, prefix=settings.API_V1_STR)
    app.include_router(search_router, prefix=settings.API_V1_STR)
    app.include_router(github_router, prefix=settings.API_V1_STR)
    app.include_router(youtube_router, prefix=settings.API_V1_STR)
    app.include_router(admin_router, prefix=settings.API_V1_STR)
    app.include_router(health_router, prefix=settings.API_V1_STR)

    @app.get("/")
    async def root():
        """Root API status endpoint."""
        return {
            "name": settings.PROJECT_NAME,
            "environment": settings.ENVIRONMENT,
            "version": "1.0.0",
            "docs_url": "/docs",
        }

    return app


app = create_app()
