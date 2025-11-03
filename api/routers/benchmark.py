"""
Benchmarking Router
Handles skill coverage analysis against job roles or custom JD
"""
import logging
from fastapi import APIRouter, HTTPException

from api.models import BenchmarkRequest, BenchmarkResponse
from backend.skills import coverage_against_role
from backend.utils import load_json

logger = logging.getLogger(__name__)
router = APIRouter()

# Load predefined roles
roles = load_json("data/roles.json")


@router.post("/benchmark", response_model=BenchmarkResponse)
async def benchmark_resume(request: BenchmarkRequest):
    """
    Calculate skill coverage against a target role or custom job description
    
    Args:
    - resume_skills: List of skills extracted from resume
    - target_role: Predefined role (e.g., "Software Engineer") OR
    - target_skills: Custom list of skills from a job description
    
    Returns:
    - Coverage percentage
    - Found skills (intersection)
    - Missing skills (gap analysis)
    """
    try:
        # Determine target skill set
        if request.target_role:
            # Use predefined role
            if request.target_role not in roles:
                available_roles = list(roles.keys())
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid role '{request.target_role}'. Available roles: {available_roles}"
                )
            target_skills = roles[request.target_role]
            target_name = request.target_role
        else:
            # Use custom JD skills
            target_skills = request.target_skills
            target_name = "Custom Job Description"
        
        logger.info(f"Benchmarking {len(request.resume_skills)} skills against {target_name}")
        
        # Calculate coverage using existing function
        coverage, missing = coverage_against_role(
            resume_skills=request.resume_skills,
            target_skills=target_skills
        )
        
        # Found skills are the intersection
        found = list(set(request.resume_skills) & set(target_skills))
        
        logger.info(f"✓ Coverage: {coverage:.1f}% ({len(found)} found, {len(missing)} missing)")
        
        return BenchmarkResponse(
            success=True,
            coverage_percentage=coverage,
            found_skills=found,
            missing_skills=missing,
            target_role=request.target_role
        )
        
    except HTTPException:
        raise  # Pass through validation errors
    except Exception as e:
        logger.error(f"Benchmark error: {e}", exc_info=True)
        return BenchmarkResponse(
            success=False,
            error=f"Benchmarking failed: {str(e)}"
        )


@router.get("/benchmark/roles")
async def get_available_roles():
    """
    Get list of predefined job roles for benchmarking
    
    Returns:
    - List of available role names
    """
    return {
        "success": True,
        "roles": list(roles.keys()),
        "count": len(roles)
    }
