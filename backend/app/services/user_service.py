import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions import NotFoundException
from app.models.user import User
from app.repositories.user_repository import UserRepository


class UserService:
    """
    Service class managing User business operations.
    """
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)

    async def get_user_by_id(self, user_id: uuid.UUID) -> User:
        """Fetches a user by ID, throwing NotFoundException if missing."""
        user = await self.user_repo.get(user_id)
        if not user:
            raise NotFoundException(message="User not found.")
        return user

    async def get_all_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Fetches all users."""
        return await self.user_repo.get_multi(skip=skip, limit=limit)

    async def delete_user(self, user_id: uuid.UUID) -> None:
        """Deletes a user from database."""
        user = await self.user_repo.get(user_id)
        if not user:
            raise NotFoundException(message="User not found.")
        await self.user_repo.remove(user_id)
