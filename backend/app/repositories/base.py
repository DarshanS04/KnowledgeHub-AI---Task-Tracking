from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
import uuid
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.base import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    """
    Generic repository pattern providing asynchronous database operation utilities.
    """
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get(self, id: uuid.UUID) -> Optional[ModelType]:
        """Gets a single model instance by its UUID ID."""
        stmt = select(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_multi(
        self, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """Gets multiple model instances with offset/limit pagination."""
        stmt = select(self.model).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, obj_in: Dict[str, Any]) -> ModelType:
        """Creates a new database model instance."""
        db_obj = self.model(**obj_in)
        self.session.add(db_obj)
        await self.session.flush() # Populates generated fields like ID and timestamps
        return db_obj

    async def update(
        self, db_obj: ModelType, obj_in: Dict[str, Any]
    ) -> ModelType:
        """Updates an existing database model instance."""
        for field, value in obj_in.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        self.session.add(db_obj)
        await self.session.flush()
        return db_obj

    async def remove(self, id: uuid.UUID) -> Optional[ModelType]:
        """Deletes a model instance by ID."""
        db_obj = await self.get(id)
        if db_obj:
            await self.session.delete(db_obj)
            await self.session.flush()
        return db_obj
