# app/config.py

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings.
    
    Reads from .env file automatically.
    If a REQUIRED setting is missing → app won't start.
    """

    # ============================================
    # Database
    # ============================================
    DATABASE_URL: str

    # ============================================
    # Redis
    # ============================================
    REDIS_URL: str

    # ============================================
    # LLM Provider
    # ============================================
    LLM_PROVIDER: str = "openrouter"

    # OpenRouter (FREE)
    OPENROUTER_API_KEY: Optional[str] = None
    OPENROUTER_MODEL: str = "arcee-ai/trinity-large-preview:free"

    # OpenAI (PAID - optional)
    OPENAI_API_KEY: Optional[str] = None

    # ============================================
    # JWT Authentication
    # ============================================
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # ============================================
    # ChromaDB (Vector Database)
    # ============================================
    CHROMA_PERSIST_DIR: str = "./chroma_data"

    # ============================================
    # App
    # ============================================
    APP_NAME: str = "DocuMind"
    DEBUG: bool = False

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    """
    Create and cache settings (singleton pattern).
    Runs only ONCE. After that returns cached result.
    """
    return Settings()