"""
PDF parsing module for SkillLens MVP
Extracts plain text from PDF files using pdfplumber (safe, no JS execution)
"""
import io
import pdfplumber
from .security import truncate_text


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extracts plain text from PDF (no JS/attachments).
    
    Uses pdfplumber which safely extracts text without executing
    embedded JavaScript or other potentially malicious content.
    
    Args:
        file_bytes: Raw PDF file content as bytes
        
    Returns:
        Extracted and truncated plain text
        
    Raises:
        Exception: If PDF is corrupted or cannot be parsed
    """
    text_parts = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            txt = page.extract_text() or ""
            text_parts.append(txt)
    full_text = "\n".join(text_parts)
    return truncate_text(full_text)
