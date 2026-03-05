# app/core/security.py

from datetime import datetime, timedelta
from jose import JWTError, jwt
import bcrypt
from app.config import get_settings

settings = get_settings()


# ============================================
# PASSWORD HASHING (using bcrypt directly)
# ============================================

def hash_password(password: str) -> str:
    """
    Hash a plain text password.
    
    Example:
        hash_password("mypassword123")
        → "$2b$12$LJ3m4ks9dKzQ8Y5n..."
    """
    # Convert string to bytes
    password_bytes = password.encode("utf-8")
    
    # Generate salt and hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    
    # Return as string
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Example:
        verify_password("mypassword123", "$2b$12$LJ3m4ks...")
        → True
    """
    try:
        password_bytes = plain_password.encode("utf-8")
        hashed_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False


# ============================================
# JWT TOKEN
# ============================================

def create_access_token(data: dict) -> str:
    """
    Create a JWT access token.
    
    Example:
        create_access_token({"sub": "user-id-123"})
        → "eyJhbGciOiJIUzI1NiIs..."
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


def decode_access_token(token: str) -> dict | None:
    """
    Decode and validate a JWT token.
    Returns token data if valid, None if invalid.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError:
        return None