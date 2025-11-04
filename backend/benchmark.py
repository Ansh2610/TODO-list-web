"""
AI Benchmarking Orchestrator
Constructs prompts, calls LLM router, validates responses
"""
import logging
from typing import Dict, List, Any, Optional

from .llm_router import LLMRouter
from .schemas import validate_ai_payload
from .redact import redact_text

logger = logging.getLogger(__name__)


def build_prompt(
    extracted_skills: List[str],
    missing_skills: List[str],
    role_name: str,
    coverage_pct: float
) -> str:
    """
    Build privacy-safe prompt from skill data only.
    
    Args:
        extracted_skills: Skills found in resume
        missing_skills: Skills needed for role but not found
        role_name: Target job role
        coverage_pct: Match percentage
        
    Returns:
        Formatted prompt string
    """
    # Limit skill counts to prevent token overflow
    extracted = extracted_skills[:50]
    missing = missing_skills[:30]
    
    prompt = f"""You are a career development expert analyzing skill alignment for a {role_name} role.

**Current Skills** ({len(extracted)}):
{', '.join(extracted) if extracted else 'None detected'}

**Missing Skills** ({len(missing)}):
{', '.join(missing) if missing else 'None - perfect match!'}

**Coverage**: {coverage_pct}%

Provide actionable career guidance in JSON format:

{{
  "coverage_explanation": "Why this coverage % happened (focus on skill gaps, not resume formatting). 2-3 sentences.",
  "top_missing_skills": "Prioritize 3-5 high-impact missing skills for this role. 1-2 sentences.",
  "learning_path": "Concrete 3-month learning roadmap with resources. 3-4 sentences.",
  "project_ideas": "2-3 portfolio project suggestions to demonstrate missing skills. 2-3 sentences.",
  "resume_tweaks": "Tactical advice on highlighting existing skills better. 2-3 sentences."
}}

Keep responses brief, specific, and actionable. Avoid generic advice."""
    
    return prompt


def get_ai_recommendations(
    extracted_skills: List[str],
    missing_skills: List[str],
    role_name: str,
    coverage_pct: float
) -> Optional[Dict[str, Any]]:
    """
    Get AI-powered career recommendations with validation.
    
    Args:
        extracted_skills: Skills detected in resume
        missing_skills: Skills needed but not present
        role_name: Target role
        coverage_pct: Match percentage
        
    Returns:
        Validated recommendation dict, or None if all providers fail
        
    Notes:
        - Never sends raw resume text to LLMs
        - Validates response against Pydantic schema
        - Silent failover across providers
    """
    try:
        # Build prompt from skill names only (never raw resume text)
        prompt = build_prompt(extracted_skills, missing_skills, role_name, coverage_pct)
        
        # Redact any PII that might have leaked into skill names
        safe_prompt = redact_text(prompt)
        
        # Call LLM router with automatic failover
        router = LLMRouter()
        raw_response = router.call(safe_prompt)
        
        # Validate against schema
        validated = validate_ai_payload(raw_response)
        
        logger.info(f"AI recommendations generated for {role_name}")
        return validated
        
    except Exception as e:
        # If LLM providers fail (network, missing packages, keys), provide
        # a deterministic, privacy-preserving fallback so the UI remains
        # useful for users during offline or dev runs.
        logger.error(f"Failed to generate AI recommendations: {type(e).__name__} - {str(e)}", exc_info=True)

        try:
            # Build a simple, deterministic fallback payload using the
            # extracted and missing skills. Keep text concise but long
            # enough to satisfy the schema validators.
            top_missing = ", ".join(missing_skills[:5]) or "None detected"
            sampled_have = ", ".join(extracted_skills[:8]) or "None"

            fallback = {
                "coverage_explanation": (
                    f"This resume matches approximately {coverage_pct}% of the typical {role_name} skills. "
                    f"The most significant gaps are: {top_missing}."
                ),
                "top_missing_skills": (
                    f"Focus on: {top_missing}. Prioritize the ones that appear most across job listings."
                ),
                "learning_path": (
                    "Month 1: Core concepts and fundamentals; "
                    "Month 2: Hands-on tutorials and small projects; "
                    "Month 3: Build a portfolio project that demonstrates missing skills."
                ),
                "project_ideas": (
                    f"Build small projects that use {top_missing} (or if none, deepen {sampled_have}). "
                    "Examples: a CRUD app, a data pipeline, or a small ML experiment depending on the gap."
                ),
                "resume_tweaks": (
                    "Bring role-relevant keywords to the top of your resume; list projects with concrete outcomes and tools used. "
                    "Quantify results where possible (e.g., reduced latency by X%, improved throughput by Y%)."
                )
            }

            # Validate using the same schema to ensure compatibility
            validated = validate_ai_payload(fallback)
            logger.info("Using deterministic fallback AI recommendations")
            return validated

        except Exception as vex:
            logger.error(f"Fallback AI generation failed: {type(vex).__name__} - {str(vex)}", exc_info=True)
            return None
