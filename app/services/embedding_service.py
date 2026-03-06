# app/services/embedding_service.py

import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
from loguru import logger
from app.config import get_settings

settings = get_settings()


class EmbeddingService:
    """
    Handles text embedding and vector storage using ChromaDB.
    
    What this does:
    1. Takes text → converts to numbers (vectors) using AI model
    2. Stores vectors in ChromaDB
    3. When user asks a question → finds similar vectors
    
    The embedding model runs LOCALLY (free, no API needed!).
    Only the LLM (answer generation) uses OpenRouter API.
    """

    def __init__(self):
        """Initialize embedding model and ChromaDB."""

        # Load embedding model (runs locally — FREE!)
        # "all-MiniLM-L6-v2" is small (80MB) but good quality
        # It converts any text into a 384-dimensional vector
        logger.info("Loading embedding model... (first time takes ~30 seconds)")
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        logger.info("✅ Embedding model loaded!")

        # Initialize ChromaDB (vector database)
        # PersistentClient saves data to disk (survives restarts)
        self.chroma_client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR,
            settings=ChromaSettings(anonymized_telemetry=False),
        )

        logger.info("✅ EmbeddingService initialized")

    def _get_collection(self, document_id: str):
        """
        Get or create a ChromaDB collection for a document.
        
        Each document gets its OWN collection.
        This keeps documents separate — searching Doc A
        won't return results from Doc B.
        """
        return self.chroma_client.get_or_create_collection(
            name=f"doc_{document_id}",
            metadata={"hnsw:space": "cosine"},  # Use cosine similarity
        )

    def store_chunks(
        self,
        document_id: str,
        chunks: list[dict],
    ) -> int:
        """
        Embed and store document chunks in vector database.
        
        Steps:
        1. Get all chunk texts
        2. Convert ALL texts to vectors at once (batch processing)
        3. Store vectors + texts in ChromaDB
        
        Args:
            document_id: UUID of the document
            chunks: List of {"text": "...", "metadata": {...}}
            
        Returns:
            Number of chunks stored
        """

        collection = self._get_collection(document_id)

        # Extract texts from chunks
        texts = [chunk["text"] for chunk in chunks]
        metadatas = [chunk["metadata"] for chunk in chunks]
        ids = [f"{document_id}_chunk_{i}" for i in range(len(chunks))]

        # Generate embeddings for ALL chunks at once
        # This is much faster than one at a time
        logger.info(f"Generating embeddings for {len(texts)} chunks...")
        embeddings = self.model.encode(texts).tolist()

        # Store in ChromaDB
        collection.add(
            documents=texts,       # Original text (for retrieval)
            embeddings=embeddings,  # Vector representations
            metadatas=metadatas,    # Extra info (chunk index, etc.)
            ids=ids,                # Unique identifiers
        )

        logger.info(
            f"✅ Stored {len(chunks)} chunks for document {document_id}"
        )
        return len(chunks)

    def search_similar(
        self,
        document_id: str,
        query: str,
        top_k: int = 5,
    ) -> list[dict]:
        """
        Find the most relevant chunks for a query.
        
        Steps:
        1. Convert query to vector
        2. Search ChromaDB for closest vectors
        3. Return the matching text chunks
        
        Args:
            document_id: Which document to search
            query: User's question
            top_k: How many results to return
            
        Returns:
            List of relevant chunks with text and distance
        """

        collection = self._get_collection(document_id)

        # Convert question to vector
        query_embedding = self.model.encode([query]).tolist()

        # Search for similar vectors in ChromaDB
        results = collection.query(
            query_embeddings=query_embedding,
            n_results=top_k,
        )

        # Format results
        similar_chunks = []
        for i in range(len(results["documents"][0])):
            similar_chunks.append({
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i],
            })

        logger.info(
            f"Found {len(similar_chunks)} relevant chunks "
            f"for: '{query[:50]}...'"
        )
        return similar_chunks

    def delete_document(self, document_id: str):
        """Delete all embeddings for a document."""
        try:
            self.chroma_client.delete_collection(f"doc_{document_id}")
            logger.info(f"Deleted embeddings for document {document_id}")
        except Exception as e:
            logger.warning(f"Could not delete collection: {e}")


# ============================================
# SINGLETON INSTANCE
# ============================================
# Created once when app starts.
# The embedding model stays in memory (fast for subsequent requests).

embedding_service = EmbeddingService()