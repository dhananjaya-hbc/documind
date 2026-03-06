# app/api/chat.py

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import json

from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.document import Conversation
from app.schemas.document import (
    QuestionRequest,
    AnswerResponse,
    ConversationResponse,
)
from app.services.document_service import DocumentService
from app.services.rag_service import RAGService

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/{document_id}/ask", response_model=AnswerResponse)
async def ask_question(
    document_id: UUID,
    request: QuestionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Ask a question about a document.
    
    🔒 Requires authentication.
    
    Send a question → Get AI answer with source citations!
    """

    # Verify document exists and belongs to user
    doc = await DocumentService.get_document(
        document_id, current_user, db
    )

    # Check document is ready
    if doc.status != "ready":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Document is still {doc.status}. Please wait.",
        )

    # Run RAG pipeline!
    result = await RAGService.ask_question(
        document_id=str(document_id),
        question=request.question,
    )

    # Save conversation to database
    conversation = Conversation(
        question=request.question,
        answer=result["answer"],
        sources=json.dumps(result["sources"]),
        document_id=document_id,
        user_id=current_user.id,
    )
    db.add(conversation)

    return AnswerResponse(
        question=request.question,
        answer=result["answer"],
        sources=result["sources"],
        document_id=document_id,
    )


@router.post("/{document_id}/ask/stream")
async def ask_question_stream(
    document_id: UUID,
    request: QuestionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Ask a question with streaming response.
    
    🔒 Requires authentication.
    
    Words appear one by one (like ChatGPT typing).
    """

    doc = await DocumentService.get_document(
        document_id, current_user, db
    )

    if doc.status != "ready":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Document is still {doc.status}. Please wait.",
        )

    async def event_stream():
        async for token in RAGService.ask_question_stream(
            document_id=str(document_id),
            question=request.question,
        ):
            yield f"data: {json.dumps({'token': token})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
    )


@router.get(
    "/{document_id}/history",
    response_model=list[ConversationResponse],
)
async def get_chat_history(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get conversation history for a document.
    
    🔒 Requires authentication.
    Returns last 50 conversations, newest first.
    """

    # Verify ownership
    await DocumentService.get_document(document_id, current_user, db)

    result = await db.execute(
        select(Conversation)
        .where(
            Conversation.document_id == document_id,
            Conversation.user_id == current_user.id,
        )
        .order_by(Conversation.created_at.desc())
        .limit(50)
    )

    conversations = result.scalars().all()
    return [
        ConversationResponse.model_validate(c)
        for c in conversations
    ]