"""
Redaction module for SkillLens
Removes PII and caps text length before sending to LLMs
"""
import re

# Regex patterns for PII detection
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE = re.compile(r"\+?\d[\d\-\s()]{7,}\d")
URL = re.compile(r"https?://\S+")
MULTISPACE = re.compile(r"\s+")


def redact_text(s: str, max_chars: int = 1800) -> str:
    """
    Redact PII from text and enforce character limit.
    
    Args:
        s: Input text to redact
        max_chars: Maximum characters to return (default: 1800 for LLM safety)
        
    Returns:
        Redacted and truncated text
    """
    if not s:
        return ""
    
    # Remove PII
    s = EMAIL.sub("[EMAIL]", s)
    s = PHONE.sub("[PHONE]", s)
    s = URL.sub("[URL]", s)
    
    # Collapse multiple spaces
    s = MULTISPACE.sub(" ", s).strip()
    
    # Hard cap for safety
    return s[:max_chars]
