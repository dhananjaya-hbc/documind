# app/api/documents.py

from uuid import UUID
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.document import DocumentResponse, DocumentListResponse
from app.services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", response_model=DocumentResponse, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a PDF document for AI processing.
    
    🔒 Requires authentication.
    
    1. Upload a PDF file
    2. Text is extracted automatically
    3. Document is chunked and embedded
    4. Ready for questions!
    """
    doc = await DocumentService.upload_document(file, current_user, db)
    return DocumentResponse.model_validate(doc)


@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all your documents.
    
    🔒 Requires authentication.
    Only shows documents YOU uploaded.
    """
    docs = await DocumentService.get_user_documents(current_user, db)
    return DocumentListResponse(
        documents=[DocumentResponse.model_validate(d) for d in docs],
        total=len(docs),
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a specific document.
    
    🔒 Requires authentication.
    Can only access YOUR documents.
    """
    doc = await DocumentService.get_document(
        document_id, current_user, db
    )
    return DocumentResponse.model_validate(doc)


@router.delete("/{document_id}", status_code=204)
async def delete_document(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a document and all its data.
    
    🔒 Requires authentication.
    Deletes: database record + vector embeddings
    """
    await DocumentService.delete_document(document_id, current_user, db)