"""
Security module for SkillLens MVP
Enforces file type validation, size limits, and safe text handling
"""
import hashlib
import mimetypes

ALLOWED_MIME = {"application/pdf"}
MAX_FILE_MB = 5
MAX_TEXT_CHARS = 100_000  # Truncate extremely long PDFs


def allowed_file(filename: str, mime: str) -> bool:
    """
    Validate that uploaded file is a PDF by extension and MIME type.
    
    Args:
        filename: Original filename from upload
        mime: MIME type reported by browser/system
        
    Returns:
        True if file passes validation, False otherwise
    """
    if not filename.lower().endswith(".pdf"):
        return False
    if mime not in ALLOWED_MIME:
        # Fallback: trust extension if mime is unknown but ends .pdf
        if mime is None and filename.lower().endswith(".pdf"):
            return True
        return False
    return True


def validate_file_size(file_bytes: bytes) -> bool:
    """
    Enforce hard file size limit.
    
    Args:
        file_bytes: Raw file content as bytes
        
    Returns:
        True if file is within limit, False otherwise
    """
    return len(file_bytes) <= MAX_FILE_MB * 1024 * 1024


def secure_hash_name(filename: str) -> str:
    """
    Generate a secure, non-identifiable filename hash.
    Prevents path traversal and PII leakage in filenames.
    
    Args:
        filename: Original filename
        
    Returns:
        16-character hexadecimal hash
    """
    return hashlib.sha256(filename.encode("utf-8")).hexdigest()[:16]


def truncate_text(text: str) -> str:
    """
    Truncate excessively long text to prevent memory/performance issues.
    
    Args:
        text: Extracted text content
        
    Returns:
        Truncated text if over limit, original text otherwise
    """
    if len(text) > MAX_TEXT_CHARS:
        return text[:MAX_TEXT_CHARS]
    return text
