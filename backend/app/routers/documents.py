from fastapi import APIRouter, Depends
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.get("")
async def list_documents(current_user: User = Depends(get_current_user)):
    """Stub list documents endpoint."""
    return {"message": "Documents list (stub)", "user": current_user.email}
