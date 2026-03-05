# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys

from app.api import auth
from app.config import get_settings

settings = get_settings()

# ============================================
# CONFIGURE LOGGING
# ============================================
logger.remove()      # Remove default logger
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
           "<level>{level: <8}</level> | "
           "<cyan>{name}</cyan>:<cyan>{function}</cyan> | "
           "<level>{message}</level>",
    level="INFO",
)

# ============================================
# CREATE FASTAPI APP
# ============================================
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered document Q&A platform",
    version="1.0.0",
    docs_url="/docs",       # Swagger UI at /docs
    redoc_url="/redoc",     # ReDoc at /redoc
)

# ============================================
# CORS MIDDLEWARE
# ============================================
#
# CORS = Cross-Origin Resource Sharing
# This allows frontends (React, etc.) on different
# domains to talk to our API.
#
# allow_origins=["*"] means "allow everyone"
# In production, you'd restrict this to your frontend URL.
#
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# INCLUDE ROUTERS
# ============================================
#
# Each router handles a group of endpoints:
#   auth router → /api/v1/auth/register, /login, /me
#   (we'll add more routers in later steps)
#
app.include_router(auth.router, prefix="/api/v1")


# ============================================
# ROOT ENDPOINTS
# ============================================

@app.get("/")
async def root():
    """Root endpoint — shows app info."""
    return {
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "docs": "/docs",
        "message": "Welcome to DocuMind API! Visit /docs for documentation.",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint — used by monitoring tools."""
    return {"status": "healthy"}