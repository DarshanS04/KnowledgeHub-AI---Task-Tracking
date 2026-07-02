from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.common import DataResponse
from app.schemas.auth import LoginRequest, RefreshRequest, SignupRequest, TokenResponse
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService
from app.middleware.rate_limiter import limiter

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/signup",
    response_model=DataResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("5/minute")
async def signup(
    request: Request,
    user_in: SignupRequest,
    db: AsyncSession = Depends(get_db),
):
    """Registers a new user account."""
    auth_service = AuthService(db)
    user = await auth_service.signup(user_in)
    return DataResponse(data=UserResponse.model_validate(user))


@router.post(
    "/login",
    response_model=DataResponse[TokenResponse],
    status_code=status.HTTP_200_OK,
)
@limiter.limit("10/minute")
async def login(
    request: Request,
    login_in: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """Authenticates credentials and returns access and refresh tokens."""
    auth_service = AuthService(db)
    token_response = await auth_service.login(login_in)
    return DataResponse(data=token_response)


@router.post(
    "/refresh",
    response_model=DataResponse[TokenResponse],
    status_code=status.HTTP_200_OK,
)
async def refresh_token(
    refresh_in: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    """Refreshes access tokens using refresh token rotation."""
    auth_service = AuthService(db)
    token_response = await auth_service.refresh_token(refresh_in)
    return DataResponse(data=token_response)


@router.post(
    "/logout",
    response_model=DataResponse[str],
    status_code=status.HTTP_200_OK,
)
async def logout(
    refresh_in: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    """Revokes the user refresh token."""
    auth_service = AuthService(db)
    await auth_service.logout(refresh_in.refresh_token)
    return DataResponse(data="Successfully logged out.")
