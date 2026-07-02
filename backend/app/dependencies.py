from typing import AsyncGenerator
from fastapi import Depends, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.core.database import get_db
from app.exceptions import ForbiddenException, UnauthorizedException
from app.models.user import User
from app.services.user_service import UserService
from app.utils.security import decode_token

# Bearer token scheme for FastAPI Swagger UI integration
security_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    FastAPI dependency injection checking JWT validation in request headers,
    returning active User instance.
    """
    if not credentials:
        raise UnauthorizedException(message="Missing authentication credentials.")

    token = credentials.credentials
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise UnauthorizedException(message="Invalid token type.")
        
        user_id = payload.get("sub")
        if not user_id:
            raise UnauthorizedException(message="Invalid token payload.")
            
    except jwt.ExpiredSignatureError:
        raise UnauthorizedException(message="Authentication token has expired.")
    except jwt.PyJWTError:
        raise UnauthorizedException(message="Could not validate credentials.")

    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id)
    
    if not user.is_active:
        raise UnauthorizedException(message="User account is deactivated.")
        
    return user


async def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    FastAPI dependency injection checking if authenticated user has admin role privileges.
    """
    if current_user.role != "admin":
        raise ForbiddenException(message="Admin permissions required for this resource.")
    return current_user
