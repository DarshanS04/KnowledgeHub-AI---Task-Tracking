from fastapi import APIRouter, Depends
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/youtube", tags=["YouTube Integration"])


@router.post("")
async def import_youtube(current_user: User = Depends(get_current_user)):
    """Stub youtube transcript import endpoint."""
    return {"message": "YouTube transcript import endpoint (stub)", "user": current_user.email}
