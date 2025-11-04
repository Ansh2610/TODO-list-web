"""
Benchmarking Router
Handles skill coverage analysis against job roles or custom JD
"""
import logging
from fastapi import APIRouter, HTTPException

from api.models import BenchmarkRequest, BenchmarkResponse
from backend.skills import coverage_against_role
from backend.utils import load_json
from backend.jd_parser import parse_jd_skills, validate_jd_text

logger = logging.getLogger(__name__)
router = APIRouter()

# Load predefined roles and skill bank
roles = load_json("data/roles.json")
skill_bank = load_json("data/skill_bank.json")


@router.post("/benchmark", response_model=BenchmarkResponse)
async def benchmark_resume(request: BenchmarkRequest):
    """
    Calculate skill coverage against a target role or custom job description
    
    Args:
    - resume_skills: List of skills extracted from resume
    - target_role: Predefined role (e.g., "Software Engineer") OR
    - target_skills: Custom list of skills from a job description OR
    - jd_text: Raw job description text (M4 feature - will be parsed)
    
    Returns:
    - Coverage percentage
    - Found skills (intersection)
    - Missing skills (gap analysis)
    """
    try:
        # Priority: jd_text > target_skills > target_role
        if request.jd_text and request.jd_text.strip():
            # M4 Feature: Parse JD text
            logger.info(f"Parsing custom JD text ({len(request.jd_text)} chars)")
            
            # Validate JD text
            is_valid, error_msg = validate_jd_text(request.jd_text)
            if not is_valid:
                raise HTTPException(status_code=400, detail=error_msg)
            
            # Parse skills from JD
            try:
                target_skills = parse_jd_skills(request.jd_text, skill_bank)
                target_name = "Custom JD"
                logger.info(f"Parsed {len(target_skills)} skills from JD")
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
                
        elif request.target_role:
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
            # Use custom JD skills list
            target_skills = request.target_skills
            target_name = "Custom Job Description"
        
        logger.info(f"Benchmarking {len(request.resume_skills)} skills against {target_name}")
        
        # Calculate coverage using existing function
        coverage, missing = coverage_against_role(
            request.resume_skills,  # extracted_flat
            target_skills           # role_skills
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
