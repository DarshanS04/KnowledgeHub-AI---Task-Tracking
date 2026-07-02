from fastapi import APIRouter, Depends
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("")
async def create_chat(current_user: User = Depends(get_current_user)):
    """Stub chat endpoint."""
    return {"message": "Chat endpoint (stub)", "user": current_user.email}
