"""
Job Description Parser
Reuses skill extraction logic to parse skills from JD text
"""
import logging
from typing import List, Dict

from .skills import extract_skills, normalize_text
from .utils import load_json

logger = logging.getLogger(__name__)

# Minimum JD length to be considered valid
MIN_JD_LENGTH = 200


def parse_jd_skills(jd_text: str, skill_bank: Dict[str, List[str]]) -> List[str]:
    """
    Extract skills from job description text.
    
    Args:
        jd_text: Raw job description text
        skill_bank: Skill categories and keywords
        
    Returns:
        Flat, unique list of skills found in JD
        
    Raises:
        ValueError: If JD text is too short or empty
    """
    if not jd_text or not jd_text.strip():
        raise ValueError("Job description cannot be empty")
    
    # Normalize and check length
    normalized = normalize_text(jd_text)
    if len(normalized) < MIN_JD_LENGTH:
        raise ValueError(f"Job description too short (minimum {MIN_JD_LENGTH} characters)")
    
    logger.info(f"Parsing JD text: {len(jd_text)} chars")
    
    # Reuse existing skill extraction
    skills_by_category = extract_skills(jd_text, skill_bank)
    
    # Flatten to unique list
    all_skills = []
    for category, skills in skills_by_category.items():
        all_skills.extend(skills)
    
    # Remove duplicates while preserving order
    unique_skills = list(dict.fromkeys(all_skills))
    
    logger.info(f"Extracted {len(unique_skills)} unique skills from JD across {len(skills_by_category)} categories")
    
    return unique_skills


def validate_jd_text(jd_text: str) -> tuple[bool, str]:
    """
    Validate job description text without parsing.
    
    Args:
        jd_text: Raw job description text
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not jd_text or not jd_text.strip():
        return False, "Job description cannot be empty"
    
    normalized = normalize_text(jd_text)
    if len(normalized) < MIN_JD_LENGTH:
        return False, f"Job description too short. Please paste at least {MIN_JD_LENGTH} characters of meaningful text."
    
    # Basic sanity check - should contain some common JD words
    common_jd_terms = ['experience', 'skills', 'requirements', 'responsibilities', 'qualifications']
    text_lower = normalized.lower()
    
    if not any(term in text_lower for term in common_jd_terms):
        return False, "This doesn't look like a job description. Please paste the full JD text including requirements and qualifications."
    
    return True, ""
