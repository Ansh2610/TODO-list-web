"""
Skills extraction and role coverage analysis for SkillLens MVP
Uses regex-based keyword matching against curated skill bank
"""
import regex as re
from typing import Dict, List, Tuple
from .utils import normalize_text


def _compile_skill_patterns(skill_bank: Dict[str, List[str]]):
    """
    Compile regex patterns for each skill category.
    
    Creates word-boundary patterns that handle special chars like + and .
    (e.g., C++, Node.js) while avoiding false matches.
    
    Args:
        skill_bank: Dict mapping category names to skill lists
        
    Returns:
        Dict mapping category names to compiled regex patterns
    """
    patterns = {}
    for cat, skills in skill_bank.items():
        pats = []
        for s in skills:
            # Escape skill name but preserve + and . for tech names
            esc = re.escape(s).replace(r"\+", "+").replace(r"\.", r"\.")
            # Word boundary pattern to avoid substring matches
            pats.append(rf"(?<![a-zA-Z0-9]){esc}(?![a-zA-Z0-9])")
        patterns[cat] = re.compile("|".join(pats), re.IGNORECASE)
    return patterns


def extract_skills(text: str, skill_bank: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """
    Extract skills from resume text by category.
    
    Args:
        text: Resume text (raw)
        skill_bank: Dict of skill categories and their keywords
        
    Returns:
        Dict mapping categories to found skills (title-cased, sorted, unique)
    """
    norm_text = normalize_text(text)
    patterns = _compile_skill_patterns(skill_bank)

    found = {cat: [] for cat in skill_bank.keys()}
    for cat, pat in patterns.items():
        matches = set(m.group(0).strip() for m in pat.finditer(norm_text))
        # Normalize to title case for consistent display
        found[cat] = sorted(set(m.title() for m in matches))
    return found


def coverage_against_role(extracted_flat: List[str], role_skills: List[str]) -> Tuple[int, List[str]]:
    """
    Calculate coverage percentage and missing skills vs. target role.
    
    Args:
        extracted_flat: List of all extracted skills (from resume)
        role_skills: List of required skills for target role
        
    Returns:
        Tuple of (coverage_percentage, list_of_missing_skills)
    """
    norm_have = set(s.lower() for s in extracted_flat)
    norm_need = [s.lower() for s in role_skills]
    hits = sum(1 for s in norm_need if s in norm_have)
    coverage = int(round((hits / max(1, len(norm_need))) * 100))
    missing = [s for s in role_skills if s.lower() not in norm_have]
    return coverage, missing


def flatten_categories(extracted: Dict[str, List[str]]) -> List[str]:
    """
    Flatten categorized skills into a single unique sorted list.
    
    Args:
        extracted: Dict of categories to skill lists
        
    Returns:
        Sorted list of unique skills across all categories
    """
    out = []
    for v in extracted.values():
        out.extend(v)
    return sorted(set(out))
