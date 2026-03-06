# app/services/llm_service.py

from loguru import logger
from app.config import get_settings

settings = get_settings()


class LLMService:
    """
    Handles interactions with the LLM (Large Language Model).
    Uses OpenRouter (free) or OpenAI (paid).
    
    This is the "Generation" part of RAG:
    - We give the LLM relevant chunks from the document
    - We give it the user's question
    - It generates an answer based on the chunks
    """

    SYSTEM_PROMPT = """You are a helpful AI assistant that answers 
questions based on the provided document context. 

Rules:
1. Only answer based on the provided context
2. If the context doesn't contain the answer, say "I couldn't find 
   this information in the document"
3. Cite which parts of the context you used
4. Be concise but thorough
5. Use bullet points for lists"""

    def __init__(self):
        """Initialize the LLM client."""

        from openai import AsyncOpenAI

        if settings.LLM_PROVIDER == "openrouter":
            self.client = AsyncOpenAI(
                api_key=settings.OPENROUTER_API_KEY,
                base_url="https://openrouter.ai/api/v1",
            )
            self.model = settings.OPENROUTER_MODEL
            logger.info(
                f"✅ Using OpenRouter (FREE) with {self.model}"
            )

        elif settings.LLM_PROVIDER == "openai":
            self.client = AsyncOpenAI(
                api_key=settings.OPENAI_API_KEY,
            )
            self.model = "gpt-4o-mini"
            logger.info("✅ Using OpenAI (PAID)")

        else:
            raise ValueError(
                f"Unknown LLM provider: {settings.LLM_PROVIDER}"
            )

    async def generate_answer(
        self,
        question: str,
        context_chunks: list[dict],
    ) -> str:
        """
        Generate an answer using the LLM.
        
        Args:
            question: User's question
            context_chunks: Relevant chunks from vector search
            
        Returns:
            AI-generated answer as string
        """

        # Build context from retrieved chunks
        context = "\n\n".join(
            f"[Source {i+1}]: {chunk['text']}"
            for i, chunk in enumerate(context_chunks)
        )

        user_prompt = f"""Context from the document:
{context}

---
Question: {question}

Please answer the question based on the context above. 
Cite your sources using [Source X] notation."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self.SYSTEM_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    },
                ],
                temperature=0.3,      # Lower = more focused/accurate
                max_tokens=1000,
            )

            answer = response.choices[0].message.content
            logger.info(f"Generated answer for: '{question[:50]}...'")
            return answer

        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            raise

    async def generate_answer_stream(
        self,
        question: str,
        context_chunks: list[dict],
    ):
        """
        Stream the answer token by token.
        Like ChatGPT typing effect.
        """

        context = "\n\n".join(
            f"[Source {i+1}]: {chunk['text']}"
            for i, chunk in enumerate(context_chunks)
        )

        user_prompt = f"""Context from the document:
{context}

---
Question: {question}

Please answer based on the context. Cite sources with [Source X]."""

        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self.SYSTEM_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    },
                ],
                temperature=0.3,
                max_tokens=1000,
                stream=True,        # Enable streaming!
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"LLM streaming failed: {e}")
            raise


# Singleton instance
llm_service = LLMService()