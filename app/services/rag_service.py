# app/services/rag_service.py

from app.services.embedding_service import embedding_service
from app.services.llm_service import llm_service
from loguru import logger


class RAGService:
    """
    Retrieval-Augmented Generation Service.
    
    This is the HEART of our application!
    
    RAG Flow:
    ┌──────────────────────────────────────────────┐
    │                                              │
    │  1. User asks: "What is mitochondria?"       │
    │         │                                    │
    │         ▼                                    │
    │  2. RETRIEVE: Search vector DB for           │
    │     chunks similar to the question           │
    │         │                                    │
    │         ▼                                    │
    │  3. AUGMENT: Add those chunks to the         │
    │     prompt as context                        │
    │         │                                    │
    │         ▼                                    │
    │  4. GENERATE: LLM reads context +            │
    │     question and generates answer            │
    │         │                                    │
    │         ▼                                    │
    │  5. Return answer with source citations      │
    │                                              │
    └──────────────────────────────────────────────┘
    """

    @staticmethod
    async def ask_question(
        document_id: str,
        question: str,
        top_k: int = 5,
    ) -> dict:
        """
        Full RAG pipeline: retrieve context → generate answer.
        
        Args:
            document_id: Which document to search
            question: User's question
            top_k: Number of chunks to retrieve
            
        Returns:
            dict with "answer" and "sources"
        """

        logger.info(f"RAG query for doc {document_id}: '{question}'")

        # ============================================
        # Step 1: RETRIEVE — Find relevant chunks
        # ============================================
        relevant_chunks = embedding_service.search_similar(
            document_id=document_id,
            query=question,
            top_k=top_k,
        )

        if not relevant_chunks:
            return {
                "answer": "No relevant information found in the document.",
                "sources": [],
            }

        # ============================================
        # Step 2 & 3: AUGMENT & GENERATE
        # ============================================
        # LLM service adds chunks to prompt (augment)
        # Then generates the answer (generate)
        answer = await llm_service.generate_answer(
            question=question,
            context_chunks=relevant_chunks,
        )

        # ============================================
        # Step 4: Format sources for citation
        # ============================================
        sources = [
            chunk["text"][:200] + "..."
            for chunk in relevant_chunks
        ]

        return {
            "answer": answer,
            "sources": sources,
        }

    @staticmethod
    async def ask_question_stream(
        document_id: str,
        question: str,
        top_k: int = 5,
    ):
        """Streaming RAG pipeline — tokens arrive one by one."""

        relevant_chunks = embedding_service.search_similar(
            document_id=document_id,
            query=question,
            top_k=top_k,
        )

        if not relevant_chunks:
            yield "No relevant information found in the document."
            return

        async for token in llm_service.generate_answer_stream(
            question=question,
            context_chunks=relevant_chunks,
        ):
            yield token