"""
Pydantic models for API request/response validation
"""
from typing import List, Optional, Dict
from pydantic import BaseModel, Field, field_validator


# ============================================================================
# Parse Endpoint Models
# ============================================================================

class ParseResponse(BaseModel):
    """Response from PDF parsing endpoint"""
    success: bool
    skills: List[str] = Field(default_factory=list)
    skills_by_category: Dict[str, List[str]] = Field(default_factory=dict)
    skill_count: int = 0
    text_preview: str = ""  # First 200 chars for debugging
    error: Optional[str] = None


# ============================================================================
# Benchmark Endpoint Models
# ============================================================================

class BenchmarkRequest(BaseModel):
    """Request for skill benchmarking"""
    resume_skills: List[str] = Field(..., min_length=1, description="Skills extracted from resume")
    target_role: Optional[str] = Field(None, description="Job role (e.g., 'Software Engineer')")
    target_skills: Optional[List[str]] = Field(None, description="Custom JD skills (alternative to role)")
    jd_text: Optional[str] = Field(None, description="Raw job description text (M4 feature)")
    
    @field_validator('target_role', 'target_skills', 'jd_text')
    @classmethod
    def validate_target(cls, v, info):
        """Ensure either target_role OR target_skills OR jd_text is provided"""
        if info.field_name == 'jd_text':
            data = info.data
            # If jd_text is provided, it takes precedence
            if v and len(v.strip()) > 0:
                return v
            # Otherwise check if we have target_role or target_skills
            if not data.get('target_role') and not data.get('target_skills'):
                raise ValueError("Must provide either target_role, target_skills, or jd_text")
        return v


class BenchmarkResponse(BaseModel):
    """Response from benchmarking endpoint"""
    success: bool
    coverage_percentage: float = 0.0
    found_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    target_role: Optional[str] = None
    error: Optional[str] = None


# ============================================================================
# AI Insights Endpoint Models
# ============================================================================

class AIRequest(BaseModel):
    """Request for AI-powered career insights"""
    found_skills: List[str] = Field(..., min_length=1)
    missing_skills: List[str] = Field(default_factory=list)
    target_role: str = Field(..., min_length=1)
    coverage_percentage: float = Field(..., ge=0.0, le=100.0)


class AIResponse(BaseModel):
    """Response from AI insights endpoint (matches backend.schemas.AIRecommendations)"""
    success: bool
    coverage_explanation: str = ""
    top_missing_skills: str = ""
    learning_path: str = ""
    project_ideas: str = ""
    resume_tweaks: str = ""
    error: Optional[str] = None


# ============================================================================
# Export Endpoint Models (M4)
# ============================================================================

class ExportRequest(BaseModel):
    """Request for exporting analysis report"""
    coverage_percent: float = Field(..., ge=0.0, le=100.0)
    missing_skills: List[str] = Field(default_factory=list)
    skills_by_category: Dict[str, List[str]] = Field(default_factory=dict)
    target_role_label: str
    mode: str = Field("Role", pattern="^(Role|Custom JD)$")
    ai_recommendations: Optional[Dict[str, str]] = None
    format: str = Field("html", pattern="^(html|json|text)$")


class ExportResponse(BaseModel):
    """Response from export endpoint"""
    success: bool
    format: str
    content: str  # HTML, JSON, or text content
    filename: str
    error: Optional[str] = None


# ============================================================================
# Roles & Learning Resources Models
# ============================================================================

class RolesResponse(BaseModel):
    """Available job roles"""
    success: bool
    roles: List[str] = Field(default_factory=list)


class LearnLinksResponse(BaseModel):
    """Learning resources for skills"""
    success: bool
    links: Dict[str, dict] = Field(default_factory=dict)  # {skill: {name, url, description}}
    error: Optional[str] = None


# ============================================================================
# Health Check
# ============================================================================

class HealthResponse(BaseModel):
    """API health status"""
    status: str = "healthy"
    version: str
    llm_providers_configured: List[str] = Field(default_factory=list)
