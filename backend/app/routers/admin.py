from fastapi import APIRouter, Depends
from app.dependencies import get_current_admin
from app.models.user import User

router = APIRouter(prefix="/admin", tags=["Admin Operations"])


@router.get("/stats")
async def get_system_stats(admin_user: User = Depends(get_current_admin)):
    """Stub admin dashboard stats endpoint."""
    return {"message": "Admin stats endpoint (stub)", "admin": admin_user.email}
