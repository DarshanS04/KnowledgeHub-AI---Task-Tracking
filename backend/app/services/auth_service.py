import logging
from datetime import datetime, timezone
import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions import AppException, UnauthorizedException
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.schemas.auth import LoginRequest, RefreshRequest, SignupRequest, TokenResponse
from app.schemas.user import UserResponse
from app.utils.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)

logger = logging.getLogger(__name__)


class AuthService:
    """
    Service class handling authentication processes including signup, login,
    refresh token rotation, and sign out revocations.
    """
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)
        self.token_repo = RefreshTokenRepository(session)

    async def signup(self, user_in: SignupRequest) -> User:
        """Registers a new user and hashes their password."""
        # Check if email exists
        existing_email = await self.user_repo.get_by_email(user_in.email)
        if existing_email:
            raise AppException(status_code=400, message="Email already registered.")

        # Check if username exists
        existing_username = await self.user_repo.get_by_username(user_in.username)
        if existing_username:
            raise AppException(status_code=400, message="Username already taken.")

        # Hash password and create user
        hashed_pw = hash_password(user_in.password)
        db_user = await self.user_repo.create({
            "email": user_in.email,
            "username": user_in.username,
            "hashed_password": hashed_pw,
            "role": "user",
            "is_active": True,
        })
        
        # Flush/commit will happen outside or dynamically in dependencies
        return db_user

    async def login(self, login_in: LoginRequest) -> TokenResponse:
        """
        Authenticates user credentials and issues short-lived access
        and long-lived refresh tokens.
        """
        user = await self.user_repo.get_by_email(login_in.email)
        if not user or not verify_password(login_in.password, user.hashed_password):
            raise UnauthorizedException(message="Incorrect email or password.")

        if not user.is_active:
            raise UnauthorizedException(message="User account is inactive.")

        # Create access and refresh tokens
        access_token = create_access_token(subject=user.id, role=user.role)
        refresh_token, token_jti, expires_at = create_refresh_token(subject=user.id)

        # Store refresh token jti hash in database
        await self.token_repo.create({
            "user_id": user.id,
            "token_hash": token_jti, # Storing JTI for fast lookup
            "expires_at": expires_at,
            "is_revoked": False,
        })

        user_resp = UserResponse.model_validate(user)
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=user_resp,
        )

    async def refresh_token(self, refresh_in: RefreshRequest) -> TokenResponse:
        """
        Rotates refresh token and issues a new pair of access/refresh tokens.
        """
        try:
            payload = decode_token(refresh_in.refresh_token)
            if payload.get("type") != "refresh":
                raise UnauthorizedException(message="Invalid token type.")
        except jwt.PyJWTError:
            raise UnauthorizedException(message="Invalid or expired refresh token.")

        token_jti = payload.get("jti")
        user_id = payload.get("sub")

        # Check in DB if revoked or expired
        db_token = await self.token_repo.get_by_hash(token_jti)
        if not db_token or db_token.is_revoked or db_token.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            # Invalidate all user tokens if a replayed or invalid refresh is used (Security Best Practice)
            if db_token:
                await self.token_repo.revoke_all_user_tokens(db_token.user_id)
            raise UnauthorizedException(message="Refresh token invalid or expired.")

        # Revoke the old refresh token (rotation)
        await self.token_repo.update(db_token, {"is_revoked": True})

        # Fetch user
        user = await self.user_repo.get(db_token.user_id)
        if not user or not user.is_active:
            raise UnauthorizedException(message="User inactive or not found.")

        # Issue new tokens
        new_access_token = create_access_token(subject=user.id, role=user.role)
        new_refresh_token, new_jti, new_expires_at = create_refresh_token(subject=user.id)

        # Save new refresh token in DB
        await self.token_repo.create({
            "user_id": user.id,
            "token_hash": new_jti,
            "expires_at": new_expires_at,
            "is_revoked": False,
        })

        user_resp = UserResponse.model_validate(user)
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            user=user_resp,
        )

    async def logout(self, refresh_token: str) -> None:
        """Revokes the refresh token."""
        try:
            payload = decode_token(refresh_token)
            token_jti = payload.get("jti")
            db_token = await self.token_repo.get_by_hash(token_jti)
            if db_token:
                await self.token_repo.update(db_token, {"is_revoked": True})
        except Exception:
            # We don't crash logout on decoding errors; just ignore it
            pass
        return None
