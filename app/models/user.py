# app/models/user.py

import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class User(Base):
    """
    Users table.
    
    Stores everyone who registers on our platform.
    
    Database table name: "users"
    
    Example row:
      id: "550e8400-e29b-41d4-a716-446655440000"
      email: "john@example.com"
      username: "john_doe"
      hashed_password: "$2b$12$LJ3m4ks..."
      is_active: True
      created_at: "2024-01-15 10:30:00"
    """

    # Table name in database
    __tablename__ = "users"

    # ============================================
    # COLUMNS
    # ============================================

    # Primary Key — unique identifier for each user
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),     # Store as UUID type
        primary_key=True,       # This is the main identifier
        default=uuid.uuid4,     # Auto-generate UUID for new users
    )

    # Email — must be unique (no two users with same email)
    email: Mapped[str] = mapped_column(
        String(255),            # Max 255 characters
        unique=True,            # No duplicates allowed
        index=True,             # Create index for fast searching
        nullable=False,         # Cannot be empty
    )

    # Username — must be unique
    username: Mapped[str] = mapped_column(
        String(100),            # Max 100 characters
        unique=True,            # No duplicates
        index=True,             # Fast searching
        nullable=False,         # Cannot be empty
    )

    # Hashed Password — NEVER store plain text!
    hashed_password: Mapped[str] = mapped_column(
        String(255),            # Hash is always ~60 chars
        nullable=False,         # Must have a password
    )

    # Is Active — can disable accounts without deleting
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,           # New users are active by default
    )

    # Created At — when the user registered
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,  # Auto-set to current time
    )

    # ============================================
    # RELATIONSHIPS
    # ============================================
    #
    # One User → Many Documents
    # "A user can upload many documents"
    #
    # back_populates="owner" means:
    #   user.documents → list of documents
    #   document.owner → the user who owns it
    #
    # cascade="all, delete-orphan" means:
    #   If we delete a user → delete all their documents too
    #
    documents = relationship(
        "Document",                  # Related model name
        back_populates="owner",      # Name in Document model
        cascade="all, delete-orphan", # Delete docs when user deleted
    )

    def __repr__(self):
        """How this object looks when printed (for debugging)."""
        return f"<User {self.username} ({self.email})>"