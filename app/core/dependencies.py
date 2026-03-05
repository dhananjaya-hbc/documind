# app/core/dependencies.py

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.core.security import decode_access_token
from app.models.user import User


# ============================================
# HTTP BEARER SCHEME
# ============================================
#
# This tells FastAPI:
# "This endpoint requires a Bearer token in the Authorization header"
#
# The request must include:
#   Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
#
# FastAPI automatically:
#   1. Checks if Authorization header exists
#   2. Extracts the token
#   3. Returns 403 if missing
#
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Extract and validate the current user from JWT token.
    
    This is a DEPENDENCY — it runs BEFORE your route function.
    
    Usage in routes:
        @router.get("/my-documents")
        async def get_docs(user: User = Depends(get_current_user)):
            # user is guaranteed to be a valid, logged-in user
            pass
    
    Flow:
        1. Extract token from Authorization header
        2. Decode the JWT token
        3. Get user_id from token
        4. Find user in database
        5. Return the user object
        
    If ANY step fails → return 401 Unauthorized
    """

    # Step 1: Get the token string
    token = credentials.credentials

    # Step 2: Decode the token
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    # Step 3: Get user_id from token payload
    user_id = payload.get("sub")    # "sub" = subject = user ID

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    # Step 4: Find user in database
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Step 5: Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )

    return user