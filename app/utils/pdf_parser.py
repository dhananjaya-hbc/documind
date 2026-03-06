# app/utils/pdf_parser.py

from pypdf import PdfReader
from loguru import logger
import io


def extract_text_from_pdf(file_content: bytes) -> str:
    """
    Extract all text from a PDF file.
    
    Args:
        file_content: Raw bytes of the PDF file
        
    Returns:
        All text from the PDF as a single string
    
    Example:
        with open("biology.pdf", "rb") as f:
            content = f.read()
        text = extract_text_from_pdf(content)
        print(text)  → "Chapter 1: The Cell..."
    """
    try:
        # Create a PDF reader from bytes
        # io.BytesIO converts bytes → file-like object
        reader = PdfReader(io.BytesIO(file_content))

        text = ""

        # Go through each page and extract text
        for page_num, page in enumerate(reader.pages):
            page_text = page.extract_text()

            if page_text:
                # Add page marker so we know where text came from
                text += f"\n--- Page {page_num + 1} ---\n"
                text += page_text

        logger.info(
            f"Extracted {len(text)} characters "
            f"from {len(reader.pages)} pages"
        )

        return text.strip()

    except Exception as e:
        logger.error(f"PDF extraction failed: {e}")
        raise ValueError(f"Failed to extract text from PDF: {e}")