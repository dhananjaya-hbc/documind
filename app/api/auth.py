# app/api/auth.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    TokenResponse,
)
from app.services.auth_service import AuthService
from app.core.dependencies import get_current_user
from app.models.user import User

# ============================================
# CREATE ROUTER
# ============================================
#
# A router groups related endpoints together.
# prefix="/auth" means all routes start with /auth
# tags=["Authentication"] groups them in API docs
#
router = APIRouter(prefix="/auth", tags=["Authentication"])


# ============================================
# REGISTER — POST /api/v1/auth/register
# ============================================
@router.post(
    "/register",
    response_model=UserResponse,   # What we return
    status_code=201,               # 201 = Created
)
async def register(
    user_data: UserCreate,                     # Pydantic validates input
    db: AsyncSession = Depends(get_db),        # Get database session
):
    """
    Register a new user account.
    
    Send:
    ```json
    {
        "email": "john@example.com",
        "username": "john_doe",
        "password": "mypassword123"
    }
    ```
    
    Returns the created user (without password).
    """
    return await AuthService.register(user_data, db)


# ============================================
# LOGIN — POST /api/v1/auth/login
# ============================================
@router.post(
    "/login",
    response_model=TokenResponse,   # Returns JWT token
)
async def login(
    user_data: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    """
    Login and receive an access token.
    
    Send:
    ```json
    {
        "email": "john@example.com",
        "password": "mypassword123"
    }
    ```
    
    Returns:
    ```json
    {
        "access_token": "eyJhbGciOi...",
        "token_type": "bearer"
    }
    ```
    
    Use the token in the Authorization header:
    `Authorization: Bearer eyJhbGciOi...`
    """
    return await AuthService.login(user_data, db)


# ============================================
# GET ME — GET /api/v1/auth/me
# ============================================
@router.get(
    "/me",
    response_model=UserResponse,
)
async def get_me(
    current_user: User = Depends(get_current_user),   # 🔒 PROTECTED!
):
    """
    Get current user profile.
    
    🔒 Requires authentication (Bearer token).
    
    This endpoint proves authentication works:
    - Send your token in the Authorization header
    - Get back your user profile
    """
    return UserResponse.model_validate(current_user)