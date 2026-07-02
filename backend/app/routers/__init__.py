from app.routers.auth import router as auth_router
from app.routers.documents import router as documents_router
from app.routers.chat import router as chat_router
from app.routers.search import router as search_router
from app.routers.github import router as github_router
from app.routers.youtube import router as youtube_router
from app.routers.admin import router as admin_router
from app.routers.health import router as health_router

__all__ = [
    "auth_router",
    "documents_router",
    "chat_router",
    "search_router",
    "github_router",
    "youtube_router",
    "admin_router",
    "health_router",
]
