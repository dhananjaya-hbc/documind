# app/schemas/user.py

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from uuid import UUID


# ============================================
# REQUEST SCHEMAS (what users SEND to us)
# ============================================

class UserCreate(BaseModel):
    """Schema for user registration."""

    email: EmailStr
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        examples=["john_doe"],
    )
    password: str = Field(
        ...,
        min_length=6,
        max_length=100,
        examples=["mypassword123"],
    )


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr
    password: str


# ============================================
# RESPONSE SCHEMAS (what we SEND BACK)
# ============================================

class UserResponse(BaseModel):
    """User data in API responses (NO password!)."""

    id: UUID
    email: str
    username: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """JWT token response after login."""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Data inside JWT token (internal use)."""

    user_id: str | None = None