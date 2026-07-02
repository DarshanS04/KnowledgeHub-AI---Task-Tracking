from fastapi import APIRouter, Depends
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/github", tags=["GitHub Integration"])


@router.post("")
async def clone_github(current_user: User = Depends(get_current_user)):
    """Stub github import endpoint."""
    return {"message": "GitHub import endpoint (stub)", "user": current_user.email}
