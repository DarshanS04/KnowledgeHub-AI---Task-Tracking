from fastapi import APIRouter, Depends
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/search", tags=["Search"])


@router.post("")
async def search(current_user: User = Depends(get_current_user)):
    """Stub search endpoint."""
    return {"message": "Search endpoint (stub)", "user": current_user.email}
