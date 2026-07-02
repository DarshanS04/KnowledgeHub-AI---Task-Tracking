from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.qdrant import get_qdrant_client
from app.schemas.common import DataResponse

router = APIRouter(prefix="/health", tags=["System Health"])


@router.get("", response_model=DataResponse[dict])
async def health_check(db: AsyncSession = Depends(get_db)):
    """Checks dependencies health state (database, vector db)."""
    db_status = "healthy"
    qdrant_status = "healthy"
    
    # Check Database connection
    try:
        await db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    # Check Qdrant connection
    try:
        client = get_qdrant_client()
        await client.get_collections()
    except Exception as e:
        qdrant_status = f"unhealthy: {str(e)}"

    overall_healthy = "unhealthy" if "unhealthy" in db_status or "unhealthy" in qdrant_status else "healthy"

    return DataResponse(
        data={
            "status": overall_healthy,
            "components": {
                "database": db_status,
                "qdrant": qdrant_status,
                "embedding_model": "loaded_on_first_use"
            }
        }
    )
