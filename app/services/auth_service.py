# app/services/auth_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserLogin,
    TokenResponse,
    UserResponse,
)
from app.core.security import hash_password, verify_password, create_access_token
from loguru import logger


class AuthService:
    """
    Handles all authentication business logic.
    
    This is the SERVICE layer — it contains the actual logic.
    Routes (API layer) call these methods.
    
    Why separate?
    - Routes handle HTTP stuff (request, response, status codes)
    - Services handle business logic (create user, verify password)
    - This separation makes code clean and testable
    """

    @staticmethod
    async def register(
        user_data: UserCreate,
        db: AsyncSession,
    ) -> UserResponse:
        """
        Register a new user.
        
        Steps:
        1. Check if email already exists
        2. Check if username already exists
        3. Hash the password
        4. Create user in database
        5. Return user data (without password)
        """

        # Step 1: Check if email already exists
        result = await db.execute(
            select(User).where(User.email == user_data.email)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        # Step 2: Check if username already exists
        result = await db.execute(
            select(User).where(User.username == user_data.username)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken",
            )

        # Step 3: Hash the password (NEVER store plain text!)
        hashed = hash_password(user_data.password)

        # Step 4: Create user
        new_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed,
        )

        db.add(new_user)
        await db.flush()          # Send to DB, get ID back
        await db.refresh(new_user)  # Reload with all fields

        logger.info(f"New user registered: {new_user.username}")

        # Step 5: Return user data (UserResponse has NO password!)
        return UserResponse.model_validate(new_user)

    @staticmethod
    async def login(
        user_data: UserLogin,
        db: AsyncSession,
    ) -> TokenResponse:
        """
        Authenticate user and return JWT token.
        
        Steps:
        1. Find user by email
        2. Verify password
        3. Create JWT token
        4. Return token
        """

        # Step 1: Find user by email
        result = await db.execute(
            select(User).where(User.email == user_data.email)
        )
        user = result.scalar_one_or_none()

        # Step 2: Verify password
        # We check BOTH conditions together for security
        # (don't tell hackers whether email or password was wrong)
        if not user or not verify_password(
            user_data.password, user.hashed_password
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        # Step 3: Create JWT token
        # "sub" (subject) is a standard JWT field for the user ID
        access_token = create_access_token(
            data={"sub": str(user.id)}
        )

        logger.info(f"User logged in: {user.username}")

        # Step 4: Return token
        return TokenResponse(access_token=access_token)