# app/utils/text_chunker.py

from loguru import logger


def chunk_text(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> list[dict]:
    """
    Split text into overlapping chunks.
    
    Why chunking?
        LLMs can only read ~4000-8000 tokens at a time.
        A 200-page PDF has ~100,000 words.
        We MUST split it into smaller pieces.
    
    Why overlap?
        If a sentence is at the boundary between two chunks,
        without overlap it would be cut in half!
        Overlap ensures we don't lose context.
    
    Args:
        text: The full document text
        chunk_size: Target size of each chunk (characters)
        chunk_overlap: How much chunks overlap
    
    Returns:
        List of dicts with 'text' and 'metadata'
    
    Example:
        text = "AAAAABBBBBCCCCC" (15 chars)
        chunk_size = 10, overlap = 5
        
        Chunk 1: "AAAAABBBBB" (chars 0-10)
        Chunk 2: "BBBBBCCCCC" (chars 5-15) ← overlaps with chunk 1!
    """

    chunks = []
    start = 0
    chunk_index = 0

    while start < len(text):
        # Calculate end position
        end = start + chunk_size

        # Try to break at a natural boundary (sentence end)
        # This prevents cutting words or sentences in half
        if end < len(text):
            # Look for the last sentence boundary in this range
            for separator in [". ", "? ", "! ", "\n\n", "\n"]:
                last_sep = text[start:end].rfind(separator)
                if last_sep != -1:
                    end = start + last_sep + len(separator)
                    break

        # Extract the chunk text
        chunk_text_content = text[start:end].strip()

        # Only add non-empty chunks
        if chunk_text_content:
            chunks.append({
                "text": chunk_text_content,
                "metadata": {
                    "chunk_index": chunk_index,
                    "start_char": start,
                    "end_char": end,
                },
            })
            chunk_index += 1

        # Move forward (with overlap)
        start = end - chunk_overlap

    logger.info(f"Created {len(chunks)} chunks from {len(text)} characters")
    return chunks