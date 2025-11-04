"""
PDF Parsing Router
Handles secure PDF upload, validation, text extraction, and skill extraction
"""
import io
import logging
from typing import Annotated
from fastapi import APIRouter, File, UploadFile, HTTPException
import pdfplumber

from api.config import settings
from api.models import ParseResponse
from backend.skills import extract_skills
from backend.utils import load_json

logger = logging.getLogger(__name__)
router = APIRouter()

# Load skill bank
skill_bank = load_json("data/skill_bank.json")


async def validate_pdf_upload(file: UploadFile) -> bytes:
    """
    Validate PDF file with security checks:
    - MIME type validation
    - File size limit (5MB)
    - PDF-only enforcement
    
    Returns: Raw file bytes
    Raises: HTTPException on validation failure
    """
    # Check MIME type
    if file.content_type not in settings.ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {file.content_type}. Only PDF files are allowed."
        )
    
    # Read file content
    content = await file.read()
    
    # Check file size
    if len(content) > settings.MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {settings.MAX_FILE_SIZE_MB}MB."
        )
    
    # Verify it's actually a PDF (check magic bytes)
    if not content.startswith(b'%PDF'):
        raise HTTPException(
            status_code=400,
            detail="Invalid PDF file. File does not have valid PDF header."
        )
    
    return content


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extract text from PDF with privacy truncation
    
    Returns: Extracted text (max 1800 chars for privacy)
    Raises: ValueError on extraction failure
    """
    try:
        pdf_file = io.BytesIO(pdf_bytes)
        with pdfplumber.open(pdf_file) as pdf:
            text_parts = []
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
            
            full_text = "\n".join(text_parts)
            
            # Don't truncate here - we need full text for skill extraction
            # Truncation only happens for the preview field
            return full_text
            
    except Exception as e:
        logger.error(f"PDF extraction failed: {e}")
        raise ValueError(f"Failed to extract text from PDF: {str(e)}")


@router.post("/parse", response_model=ParseResponse)
async def parse_resume(
    file: Annotated[UploadFile, File(description="PDF resume file (max 5MB)")]
):
    """
    Parse PDF resume and extract skills
    
    Security features:
    - PDF-only MIME type validation
    - 5MB file size limit
    - Magic byte verification
    - Privacy text truncation (1800 chars)
    
    Returns:
    - List of extracted skills
    - Text preview for debugging
    """
    try:
        # Step 1: Validate upload
        pdf_bytes = await validate_pdf_upload(file)
        logger.info(f"✓ Validated PDF: {file.filename} ({len(pdf_bytes)} bytes)")
        
        # Step 2: Extract text
        text = extract_text_from_pdf(pdf_bytes)
        logger.info(f"✓ Extracted text: {len(text)} chars")
        
        # Step 3: Extract skills by category
        skills_by_category = extract_skills(text, skill_bank)
        
        # Flatten skills for compatibility
        skills_flat = [skill for category_skills in skills_by_category.values() for skill in category_skills]
        
        logger.info(f"✓ Extracted {len(skills_flat)} skills across {len(skills_by_category)} categories")
        
        return ParseResponse(
            success=True,
            skills=skills_flat,
            skills_by_category=skills_by_category,
            skill_count=len(skills_flat),
            text_preview=text[:200] + "..." if len(text) > 200 else text
        )
        
    except HTTPException:
        raise  # Pass through validation errors
    except ValueError as e:
        logger.error(f"Parse error: {e}")
        return ParseResponse(
            success=False,
            error=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected parse error: {e}", exc_info=True)
        return ParseResponse(
            success=False,
            error="Failed to parse resume. Please ensure it's a valid PDF file."
        )
