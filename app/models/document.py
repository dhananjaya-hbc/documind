# app/models/document.py

import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, Integer, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class Document(Base):
    """
    Documents table.
    
    Stores information about uploaded PDFs.
    
    Example row:
      id: "660e8400-..."
      title: "Biology Textbook"
      filename: "biology.pdf"
      content: "Chapter 1: The Cell is the basic unit..."  (first 5000 chars)
      chunk_count: 45
      status: "ready"
      owner_id: "550e8400-..."  (links to User)
      created_at: "2024-01-15"
    """

    __tablename__ = "documents"

    # ============================================
    # COLUMNS
    # ============================================

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Document title (extracted from filename)
    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    # Original filename
    filename: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    # Extracted text content (first 5000 chars as preview)
    # Text type = unlimited length (unlike String which has max)
    content: Mapped[str] = mapped_column(
        Text,
        nullable=True,     # Empty until processing completes
    )

    # How many chunks this document was split into
    chunk_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    # Processing status
    # "processing" → PDF is being processed
    # "ready"      → Ready for questions
    # "failed"     → Something went wrong
    status: Mapped[str] = mapped_column(
        String(50),
        default="processing",
    )

    # Foreign Key — WHO uploaded this document?
    # Links to users.id
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),     # Points to users table, id column
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    # ============================================
    # RELATIONSHIPS
    # ============================================

    # Many Documents → One User (who owns this document)
    # back_populates="documents" connects to User.documents
    owner = relationship(
        "User",
        back_populates="documents",
    )

    # One Document → Many Conversations
    conversations = relationship(
        "Conversation",
        back_populates="document",
        cascade="all, delete-orphan",  # Delete chats when doc deleted
    )

    def __repr__(self):
        return f"<Document {self.title} ({self.status})>"


class Conversation(Base):
    """
    Conversations table.
    
    Stores every question asked and answer received.
    This gives us CHAT HISTORY.
    
    Example row:
      id: "770e8400-..."
      question: "What is mitochondria?"
      answer: "Mitochondria is the powerhouse of the cell..."
      sources: '[\"Chapter 3 says...\", \"Page 45 mentions...\"]'
      document_id: "660e8400-..."  (links to Document)
      user_id: "550e8400-..."      (links to User)
      created_at: "2024-01-15"
    """

    __tablename__ = "conversations"

    # ============================================
    # COLUMNS
    # ============================================

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # The question user asked
    question: Mapped[str] = mapped_column(
        Text,               # Text = unlimited length
        nullable=False,
    )

    # The AI's answer
    answer: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # Source chunks used (stored as JSON string)
    # Example: '["The cell is...", "Chapter 3 explains..."]'
    sources: Mapped[str] = mapped_column(
        Text,
        nullable=True,      # Might not always have sources
    )

    # Foreign Key — WHICH document was this question about?
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id"),
        nullable=False,
    )

    # Foreign Key — WHO asked this question?
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    # ============================================
    # RELATIONSHIPS
    # ============================================

    # Many Conversations → One Document
    document = relationship(
        "Document",
        back_populates="conversations",
    )

    def __repr__(self):
        return f"<Conversation Q: {self.question[:50]}...>"