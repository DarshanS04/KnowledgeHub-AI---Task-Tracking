import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.auth_service import AuthService
from app.schemas.auth import LoginRequest, SignupRequest
from app.exceptions import AppException


@pytest.mark.asyncio
async def test_signup_already_exists():
    session = AsyncMock()
    
    # Mock UserRepository
    auth_service = AuthService(session)
    auth_service.user_repo = AsyncMock()
    
    # Simulate existing user
    auth_service.user_repo.get_by_email.return_value = MagicMock()
    
    request = SignupRequest(
        email="test@domain.com",
        username="testuser",
        password="securepassword123"
    )
    
    with pytest.raises(AppException) as exc_info:
        await auth_service.signup(request)
        
    assert exc_info.value.status_code == 400
    assert "already registered" in exc_info.value.message
