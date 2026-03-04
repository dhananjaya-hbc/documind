# app/database.py

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase
from app.config import get_settings

settings = get_settings()


# ============================================
# 1. ENGINE — Connection to PostgreSQL
# ============================================
#
# Think of engine as a BRIDGE:
#   Your Python code ←→ Engine ←→ PostgreSQL
#
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,   # If True → prints SQL queries (helpful for learning!)
    pool_size=20,          # Keep 20 connections ready (like 20 phone lines)
    max_overflow=10,       # Allow 10 extra if all 20 are busy
)


# ============================================
# 2. SESSION FACTORY — Creates database sessions
# ============================================
#
# Session = One conversation with the database
#
# Like a shopping cart:
#   session.add(user)     ← Put in cart
#   session.commit()      ← Checkout (save)
#   session.rollback()    ← Cancel (undo)
#   session.close()       ← Leave store
#
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ============================================
# 3. BASE CLASS — Parent for all database tables
# ============================================
#
# Every table we create will inherit from this:
#
#   class User(Base):         ← User IS a database table
#       __tablename__ = "users"
#
#   class Document(Base):     ← Document IS a database table
#       __tablename__ = "documents"
#
class Base(DeclarativeBase):
    pass


# ============================================
# 4. GET_DB — Dependency for FastAPI routes
# ============================================
#
# Every API route that needs the database will use this:
#
#   @app.get("/users")
#   async def get_users(db: AsyncSession = Depends(get_db)):
#       # db is ready to use!
#       pass
#
async def get_db() -> AsyncSession:
    """
    Creates a database session for each request.
    
    Automatically:
    - Opens a connection
    - Gives it to your route (yield)
    - Commits if everything went well
    - Rolls back if there was an error
    - Closes the connection
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session            # Give session to route
            await session.commit()   # Save changes if no error
        except Exception:
            await session.rollback() # Undo changes if error
            raise
        finally:
            await session.close()    # Always close connection