"""
Resources Router
Provides job roles list and learning resources
"""
import logging
from fastapi import APIRouter

from api.models import RolesResponse, LearnLinksResponse
from backend.utils import load_json

logger = logging.getLogger(__name__)
router = APIRouter()

# Load predefined roles
roles = load_json("data/roles.json")


@router.get("/roles", response_model=RolesResponse)
async def get_roles():
    """
    Get all available predefined job roles
    
    Returns:
    - List of role names for benchmarking
    """
    return RolesResponse(
        success=True,
        roles=sorted(roles.keys())
    )


@router.get("/learn-links/{skill}", response_model=LearnLinksResponse)
async def get_learning_links(skill: str):
    """
    Get learning resources for a specific skill
    
    Args:
    - skill: Skill name (e.g., "Python", "Docker")
    
    Returns:
    - List of curated learning resources with title, URL, and type
    
    Note: This is a placeholder for Milestone 4.
    Will be populated with actual learning resource database.
    """
    # TODO: Implement learning resource database in M4
    logger.info(f"Learning resources requested for: {skill}")
    
    # Placeholder response
    placeholder_links = [
        {
            "title": f"Learn {skill} - Official Documentation",
            "url": f"https://www.google.com/search?q={skill}+official+documentation",
            "type": "documentation"
        },
        {
            "title": f"{skill} Tutorial on freeCodeCamp",
            "url": f"https://www.freecodecamp.org/search?query={skill}",
            "type": "tutorial"
        },
        {
            "title": f"{skill} Course on Coursera",
            "url": f"https://www.coursera.org/search?query={skill}",
            "type": "course"
        }
    ]
    
    return LearnLinksResponse(
        success=True,
        skill=skill,
        links=placeholder_links
    )
