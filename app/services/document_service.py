# app/services/document_service.py

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status, UploadFile

from app.models.document import Document
from app.models.user import User
from app.utils.pdf_parser import extract_text_from_pdf
from app.utils.text_chunker import chunk_text
from app.services.embedding_service import embedding_service
from loguru import logger


class DocumentService:
    """
    Handles document upload, processing, and management.
    
    Upload Flow:
    1. User uploads PDF file
    2. We extract text from PDF
    3. We split text into chunks
    4. We embed chunks and store in ChromaDB
    5. We save document info in PostgreSQL
    6. Document is ready for questions!
    """

    @staticmethod
    async def upload_document(
        file: UploadFile,
        user: User,
        db: AsyncSession,
    ) -> Document:
        """
        Upload and process a document.
        
        Args:
            file: Uploaded PDF file
            user: Current logged-in user
            db: Database session
            
        Returns:
            Document model with status="ready"
        """

        # ============================================
        # Step 1: Validate file
        # ============================================
        if not file.filename.endswith(".pdf"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are supported. Please upload a .pdf file.",
            )

        # Read file content
        content = await file.read()

        # Check file size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB in bytes
        if len(content) > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size must be under 10MB.",
            )

        # ============================================
        # Step 2: Create document record in database
        # ============================================
        doc = Document(
            title=file.filename.rsplit(".", 1)[0],  # Remove .pdf extension
            filename=file.filename,
            status="processing",
            owner_id=user.id,
        )
        db.add(doc)
        await db.flush()        # Get the ID
        await db.refresh(doc)   # Load all fields

        try:
            # ============================================
            # Step 3: Extract text from PDF
            # ============================================
            logger.info(f"📄 Extracting text from {file.filename}")
            text = extract_text_from_pdf(content)

            if not text.strip():
                raise ValueError(
                    "No text could be extracted from the PDF. "
                    "The file might be scanned images."
                )

            # ============================================
            # Step 4: Chunk the text
            # ============================================
            logger.info("✂️ Chunking text...")
            chunks = chunk_text(
                text,
                chunk_size=1000,
                chunk_overlap=200,
            )

            # ============================================
            # Step 5: Embed and store chunks
            # ============================================
            logger.info("🧮 Generating embeddings...")
            chunk_count = embedding_service.store_chunks(
                document_id=str(doc.id),
                chunks=chunks,
            )

            # ============================================
            # Step 6: Update document record
            # ============================================
            doc.content = text[:5000]      # Store preview (first 5000 chars)
            doc.chunk_count = chunk_count
            doc.status = "ready"

            logger.info(
                f"✅ Document processed: {file.filename} "
                f"({chunk_count} chunks)"
            )

        except Exception as e:
            doc.status = "failed"
            logger.error(f"❌ Document processing failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to process document: {str(e)}",
            )

        return doc

    @staticmethod
    async def get_user_documents(
        user: User,
        db: AsyncSession,
    ) -> list[Document]:
        """Get all documents for a user."""

        result = await db.execute(
            select(Document)
            .where(Document.owner_id == user.id)
            .order_by(Document.created_at.desc())  # Newest first
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_document(
        document_id: UUID,
        user: User,
        db: AsyncSession,
    ) -> Document:
        """
        Get a specific document.
        Also checks that the document belongs to the user!
        """

        result = await db.execute(
            select(Document).where(
                Document.id == document_id,
                Document.owner_id == user.id,  # Security check!
            )
        )
        doc = result.scalar_one_or_none()

        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )
        return doc

    @staticmethod
    async def delete_document(
        document_id: UUID,
        user: User,
        db: AsyncSession,
    ):
        """Delete a document and its embeddings."""

        # Get document (also checks ownership)
        doc = await DocumentService.get_document(document_id, user, db)

        # Delete embeddings from ChromaDB
        embedding_service.delete_document(str(document_id))

        # Delete from PostgreSQL
        await db.delete(doc)

        logger.info(f"🗑️ Deleted document: {doc.title}")