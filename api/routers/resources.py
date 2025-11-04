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

# Load predefined roles and learning links
roles = load_json("data/roles.json")
learn_links = load_json("data/learn_links.json")


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


@router.get("/learn-links", response_model=LearnLinksResponse)
async def get_learning_links():
    """
    Get all curated learning resources (M4 feature)
    
    Returns:
    - Dictionary of skill -> {name, url, description} mappings
    - Includes ~60 common tech skills with official docs/tutorials
    """
    logger.info(f"Learning links requested - returning {len(learn_links)} resources")
    
    return LearnLinksResponse(
        success=True,
        links=learn_links
    )

