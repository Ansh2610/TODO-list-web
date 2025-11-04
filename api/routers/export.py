"""
Export Router
Generate privacy-safe analysis reports (HTML/JSON/Text)
"""
import logging
from fastapi import APIRouter, HTTPException

from api.models import ExportRequest, ExportResponse
from backend.exporter import (
    create_export_payload,
    to_json,
    to_text_report,
    generate_html_report
)
from backend.flags import ENABLE_EXPORT_REPORT

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/export", response_model=ExportResponse)
async def export_report(request: ExportRequest):
    """
    Generate privacy-safe one-pager report
    
    Args:
    - coverage_percent: Match percentage
    - missing_skills: Gap analysis
    - skills_by_category: Categorized skills
    - target_role_label: Role name or "Custom JD"
    - mode: "Role" or "Custom JD"
    - ai_recommendations: AI insights (optional)
    - format: "html", "json", or "text"
    
    Returns:
    - Formatted report content with no PII
    """
    if not ENABLE_EXPORT_REPORT:
        raise HTTPException(
            status_code=403,
            detail="Export feature is currently disabled"
        )
    
    try:
        logger.info(f"Generating {request.format} export for {request.target_role_label}")
        
        # Create privacy-safe payload
        payload = create_export_payload(
            coverage_percent=request.coverage_percent,
            missing_skills=request.missing_skills,
            skills_by_category=request.skills_by_category,
            ai_recommendations=request.ai_recommendations,
            target_role_label=request.target_role_label,
            mode=request.mode
        )
        
        # Generate requested format
        if request.format == "json":
            content = to_json(payload)
            filename = f"skilllens_report_{request.target_role_label.replace(' ', '_')}.json"
        elif request.format == "text":
            content = to_text_report(payload)
            filename = f"skilllens_report_{request.target_role_label.replace(' ', '_')}.txt"
        else:  # html
            content = generate_html_report(payload)
            filename = f"skilllens_report_{request.target_role_label.replace(' ', '_')}.html"
        
        logger.info(f"✓ Generated {request.format} report ({len(content)} bytes)")
        
        return ExportResponse(
            success=True,
            format=request.format,
            content=content,
            filename=filename
        )
        
    except Exception as e:
        logger.error(f"Export generation failed: {e}", exc_info=True)
        return ExportResponse(
            success=False,
            format=request.format,
            content="",
            filename="",
            error=f"Failed to generate report: {str(e)}"
        )
