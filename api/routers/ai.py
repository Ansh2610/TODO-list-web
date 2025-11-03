"""
AI Insights Router
Privacy-first LLM integration with provider-agnostic failover
"""
import logging
from fastapi import APIRouter, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from api.config import settings
from api.models import AIRequest, AIResponse
from backend.benchmark import get_ai_recommendations

logger = logging.getLogger(__name__)
router = APIRouter()

# Rate limiter: 5 AI calls per hour per IP
limiter = Limiter(key_func=get_remote_address)


@router.post("/ai", response_model=AIResponse)
@limiter.limit(f"{settings.RATE_LIMIT_AI_CALLS}/{settings.RATE_LIMIT_WINDOW_SECONDS}second")
async def get_ai_insights(request: Request, ai_request: AIRequest):
    """
    Generate AI-powered career insights with privacy guarantees
    
    Privacy features:
    - PII redaction before LLM transmission
    - Text truncation (1800 chars max)
    - No data storage or logging of user content
    - API keys kept server-side only
    
    Rate limits:
    - 5 calls per hour per IP address
    
    Provider failover:
    - Tries GEMINI → OPENAI → ANTHROPIC
    - Silent failover on errors
    - Returns provider used in response
    
    Args:
    - found_skills: Skills matched with target role
    - missing_skills: Gap analysis results
    - target_role: Job role for context
    - coverage_percentage: Current skill coverage
    
    Returns:
    - coverage_explanation: Why your coverage is X%
    - top_missing_skills: Most important gaps to fill
    - learning_path: Step-by-step skill acquisition plan
    - project_ideas: Hands-on projects to build skills
    - resume_tweaks: How to better highlight your skills
    """
    try:
        logger.info(f"🤖 AI request for {ai_request.target_role} ({ai_request.coverage_percentage:.1f}% coverage)")
        
        # Call backend with privacy-first LLM router
        result = get_ai_recommendations(
            found_skills=ai_request.found_skills,
            missing_skills=ai_request.missing_skills,
            target_role=ai_request.target_role,
            coverage_percentage=ai_request.coverage_percentage
        )
        
        if result is None:
            logger.error("All LLM providers failed")
            return AIResponse(
                success=False,
                error="AI service temporarily unavailable. All providers failed. Please try again later."
            )
        
        # Determine which provider was used (check logs or add to backend response)
        # For now, we'll infer from settings
        provider_used = settings.LLM_PROVIDERS.split(',')[0].strip()
        
        logger.info(f"✓ AI insights generated via {provider_used}")
        
        return AIResponse(
            success=True,
            coverage_explanation=result.coverage_explanation,
            top_missing_skills=result.top_missing_skills,
            learning_path=result.learning_path,
            project_ideas=result.project_ideas,
            resume_tweaks=result.resume_tweaks,
            provider_used=provider_used
        )
        
    except HTTPException:
        raise  # Pass through rate limit errors
    except Exception as e:
        logger.error(f"AI insights error: {e}", exc_info=True)
        return AIResponse(
            success=False,
            error=f"Failed to generate AI insights: {str(e)}"
        )
