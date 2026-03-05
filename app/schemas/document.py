# app/schemas/document.py

from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID


class DocumentResponse(BaseModel):
    """Document info in API responses."""

    id: UUID
    title: str
    filename: str
    chunk_count: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """List of documents."""

    documents: list[DocumentResponse]
    total: int


class QuestionRequest(BaseModel):
    """User's question about a document."""

    question: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        examples=["What is this document about?"],
    )


class AnswerResponse(BaseModel):
    """AI answer with sources."""

    question: str
    answer: str
    sources: list[str]
    document_id: UUID


class ConversationResponse(BaseModel):
    """Chat history item."""

    id: UUID
    question: str
    answer: str
    sources: str | None
    created_at: datetime

    class Config:
        from_attributes = True