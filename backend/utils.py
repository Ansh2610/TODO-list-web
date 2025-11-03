"""
Utility functions for SkillLens MVP
Handles JSON loading, stopwords, and text normalization
"""
import json
import re
from unidecode import unidecode


def load_json(path: str):
    """
    Load and parse JSON file.
    
    Args:
        path: File path to JSON file
        
    Returns:
        Parsed JSON content (dict or list)
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_stopwords(path: str):
    """
    Load stopwords from text file (one per line).
    
    Args:
        path: File path to stopwords file
        
    Returns:
        Set of lowercase stopwords
    """
    with open(path, "r", encoding="utf-8") as f:
        return set(w.strip().lower() for w in f if w.strip())


def normalize_text(text: str) -> str:
    """
    Normalize text for skill matching.
    
    Process:
    1. Convert Unicode to ASCII (handles accents, special chars)
    2. Collapse multiple whitespace to single space
    3. Lowercase and trim
    
    Args:
        text: Raw text to normalize
        
    Returns:
        Normalized text suitable for regex matching
    """
    # ASCII fold (e.g., café → cafe)
    text = unidecode(text)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()
