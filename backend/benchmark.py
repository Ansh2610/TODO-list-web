"""
AI Benchmarking Orchestrator
Constructs prompts, calls LLM router, validates responses
"""
import logging
from typing import Dict, List, Any, Optional

from .llm_router import LLMRouter
from .schemas import validate_ai_payload

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

Provide detailed, actionable career guidance in JSON format with SPECIFIC learning resources:

{{
  "coverage_explanation": "Detailed explanation of why this coverage % happened. Analyze the skill gaps in context of the {role_name} role requirements. Explain which skill categories are strong vs weak. 4-5 sentences with specific examples.",
  
  "top_missing_skills": "Prioritize the top 5 most critical missing skills for this {role_name} role. For EACH skill, explain:
- Why it's important for this role (1 sentence)
- Recommended learning resources with FULL URLs:
  * Online courses (Coursera, Udemy, Pluralsight, edX with specific course names and URLs)
  * Official documentation (with exact URLs)
  * YouTube tutorials (specific channel/playlist names and URLs)
  * Books (title and author)
- Estimated time to learn (e.g., '2-3 weeks with 5 hours/week')
Format as: 'Skill Name: [importance] | Learn: [Course Name](URL), [Doc Name](URL) | Time: X weeks'",

  "learning_path": "Detailed 3-6 month learning roadmap broken down by:
- Month 1-2: [Skills to focus on] with specific course links
- Month 3-4: [Next skills] with specific course links  
- Month 5-6: [Advanced skills] with specific course links
Include 2-3 specific learning resources (with URLs) for each phase. Recommend certifications if relevant (e.g., 'AWS Certified Developer: https://aws.amazon.com/certification/'). Suggest weekly time commitment (e.g., '10-15 hours/week').",

  "project_ideas": "Provide 3-4 specific portfolio project ideas that demonstrate the missing skills:
- Project 1: [Name] - [Description] | Tech stack: [specific technologies] | Complexity: [Beginner/Intermediate/Advanced] | GitHub templates or similar projects: [URLs if available] | Key learning outcomes: [skills demonstrated]
- Project 2: [similar format]
Include links to GitHub repositories with similar implementations, tutorial series, or project starter templates where possible.",

  "resume_tweaks": "Tactical advice on improving resume presentation:
- How to better highlight existing skills (specific formatting tips, keywords to add)
- Which projects/experience to emphasize for {role_name} roles
- Recommended resume sections (e.g., 'Add Technical Skills section', 'Create Projects portfolio')
- ATS optimization tips (keywords to include based on missing skills)
- Specific action items (e.g., 'Add GitHub link prominently', 'Quantify achievements with metrics')
5-6 specific, actionable recommendations."
}}

CRITICAL REQUIREMENTS:
1. Include REAL, CLICKABLE URLs for all learning resources (courses, docs, certifications)
2. Be SPECIFIC - name actual courses, not "take a course in X"
3. Provide MEASURABLE timelines (weeks, hours/week)
4. Include CONCRETE project examples with tech stacks
5. Make every recommendation ACTIONABLE with clear next steps

Example URL formats:
- Coursera: https://www.coursera.org/learn/[course-name]
- Udemy: https://www.udemy.com/course/[course-name]
- Official docs: https://docs.[technology].com/
- YouTube: https://www.youtube.com/playlist?list=[id]
- GitHub: https://github.com/[user]/[repo]"""
    
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
        
        # Prompt is already privacy-safe (skills only, no PII)
        # No need for additional redaction
        
        # Call LLM router with automatic failover
        router = LLMRouter()
        raw_response = router.call(prompt)
        
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
