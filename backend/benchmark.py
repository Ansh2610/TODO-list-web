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
  "coverage_explanation": "Write 4-6 detailed sentences explaining why this coverage % happened. Analyze the skill gaps in context of the {role_name} role requirements. Explain which skill categories (e.g., backend, frontend, DevOps, databases) are strong vs weak with specific examples. Mention 2-3 specific missing skills and why they matter. Include industry context about what employers expect.",
  
  "top_missing_skills": "List the top 5 most critical missing skills for this {role_name} role. For EACH skill, you MUST include:
1. Skill name in **bold**
2. Why it's important (2-3 sentences with specific job market data or role requirements)
3. At least 3 learning resources in markdown link format [Course Name](https://full-url.com) 🔗
   - Include Udemy/Coursera courses with REAL course names
   - Include official documentation with REAL URLs
   - Include YouTube tutorials with REAL channel/video URLs
4. Realistic time estimate with hours/week (e.g., '3 weeks with 10 hours/week')

Write 4-5 sentences per skill. Include URLs in every entry.",

  "learning_path": "Create a detailed 6-month learning roadmap (6-8 sentences total). Break it down into 3 phases:

**Months 1-2**: [List 2-3 foundational skills to learn first]. Recommend 2-3 specific courses with FULL URLs in markdown format [Course](https://url.com) 🔗. Include estimated hours/week.

**Months 3-4**: [List 2-3 intermediate skills building on foundations]. Recommend 2-3 specific courses with FULL URLs. Suggest certifications like '[AWS Certified Developer](https://aws.amazon.com/certification/certified-developer-associate/) 🔗' if relevant.

**Months 5-6**: [List 2-3 advanced skills or specializations]. Recommend 2-3 advanced courses/resources with FULL URLs. Include capstone project suggestions.

Include weekly time commitment estimate (e.g., '12-15 hours/week'). MUST include at least 6-8 real course URLs total.",

  "project_ideas": "Provide 3-4 detailed portfolio project ideas (4-5 sentences each). For EACH project include:
- **Project Name**: Descriptive title
- **Description**: What it does and why it's valuable (2-3 sentences)
- **Tech Stack**: List 4-6 specific technologies (e.g., 'React, Node.js, PostgreSQL, Docker, AWS')
- **Complexity**: Beginner/Intermediate/Advanced
- **Key Learning Outcomes**: List 3-4 specific skills demonstrated
- **Resources**: Include 2-3 markdown links to GitHub templates, tutorials, or similar projects [Example](https://github.com/url) 🔗
- **Timeline**: Estimated hours to complete (e.g., '20-30 hours over 3 weeks')

Write detailed descriptions, not brief summaries.",

  "resume_tweaks": "Provide 6-8 specific, actionable resume optimization tips (6-8 sentences total):
- How to reword experience bullets to highlight technical skills (give 1-2 specific examples)
- Which keywords to add for ATS optimization (list 5-6 specific keywords for {role_name})
- Resume section recommendations (e.g., 'Add a Technical Skills section at top', 'Create a Projects portfolio section')
- How to quantify achievements (give 2 specific examples with numbers/metrics)
- Formatting tips for readability (specific font, spacing, section order advice)
- How to highlight relevant projects/experience for {role_name} roles (specific guidance)

Be specific with examples, not generic advice like 'improve your resume'."
}}

CRITICAL REQUIREMENTS - YOU MUST FOLLOW THESE:
1. EVERY skill MUST have at least 2-3 REAL, WORKING URLs in markdown format [Text](URL)
2. Use ACTUAL course names: "Complete Python Bootcamp" not "a Python course"
3. Include REAL website URLs: https://www.coursera.org/learn/python, https://docs.python.org/
4. Add SPECIFIC time estimates: "3 weeks with 10 hours/week" not "a few weeks"
5. For projects, include FULL descriptions (3-4 sentences) with tech stacks
6. Every section MUST be 4-6 sentences minimum, not 1-2 sentences

EXAMPLE FORMAT (YOU MUST FOLLOW THIS STRUCTURE):

For top_missing_skills:
"**Docker**: Critical for containerization and deployment in DevOps roles. Docker skills are required for 85% of backend positions.
Learn: [Docker Mastery: with Kubernetes +Swarm from a Docker Captain](https://www.udemy.com/course/docker-mastery/) 🔗, [Official Docker Documentation](https://docs.docker.com/) 🔗, [FreeCodeCamp Docker Tutorial](https://www.youtube.com/watch?v=fqMOX6JJhGo) 🔗
Time: 2-3 weeks with 8-10 hours/week"

For learning_path:
"**Months 1-2**: Focus on foundational backend skills - learn Go programming and RESTful API design. Take [Go: The Complete Developer's Guide](https://www.udemy.com/course/go-the-complete-developers-guide/) 🔗 and build 2-3 small APIs. Study [Official Go Documentation](https://go.dev/doc/) 🔗. Get certified with [Go Programming Language Specialization](https://www.coursera.org/specializations/google-golang) 🔗. Time commitment: 12-15 hours/week."

For project_ideas:
"**Project 1: Task Management REST API**
Build a full-featured task management system with user authentication, CRUD operations, and database integration. 
**Tech Stack**: Go (Gin framework), PostgreSQL, Docker, JWT authentication, Redis for caching
**Complexity**: Intermediate
**Learning Outcomes**: RESTful API design, database modeling, authentication, containerization
**Resources**: [Gin Web Framework Guide](https://github.com/gin-gonic/gin) 🔗, [PostgreSQL Tutorial](https://www.postgresqltutorial.com/) 🔗, [Similar Project Example](https://github.com/gothinkster/golang-gin-realworld-example-app) 🔗
**Timeline**: 3-4 weeks, 15-20 hours total"

YOU MUST INCLUDE REAL URLS IN EVERY SECTION. NO GENERIC ADVICE.

IMPORTANT: Your response will NOT be truncated. You have 4096 tokens available. Write FULL, DETAILED, COMPREHENSIVE responses for each section. DO NOT abbreviate or summarize. Provide COMPLETE information with ALL URLs requested."""
    
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
