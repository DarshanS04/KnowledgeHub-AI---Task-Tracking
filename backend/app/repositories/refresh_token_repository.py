from typing import Optional
import uuid
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.refresh_token import RefreshToken
from app.repositories.base import BaseRepository


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    """
    Repository class handling refresh token database interactions, rotations,
    and revocations.
    """
    def __init__(self, session: AsyncSession):
        super().__init__(RefreshToken, session)

    async def get_by_hash(self, token_hash: str) -> Optional[RefreshToken]:
        """Gets a refresh token record matching the hashed token string."""
        stmt = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def revoke_all_user_tokens(self, user_id: uuid.UUID) -> None:
        """Revokes all active refresh tokens associated with a given user ID."""
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.is_revoked == False)
            .values(is_revoked=True)
        )
        await self.session.execute(stmt)
