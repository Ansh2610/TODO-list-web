"""
Pydantic models for API request/response validation
"""
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


# ============================================================================
# Parse Endpoint Models
# ============================================================================

class ParseResponse(BaseModel):
    """Response from PDF parsing endpoint"""
    success: bool
    skills: List[str] = Field(default_factory=list)
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
    
    @field_validator('target_role', 'target_skills')
    @classmethod
    def validate_target(cls, v, info):
        """Ensure either target_role OR target_skills is provided"""
        if info.field_name == 'target_skills':
            # Check if we have at least one target specified
            data = info.data
            if not v and not data.get('target_role'):
                raise ValueError("Must provide either target_role or target_skills")
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
    provider_used: Optional[str] = None  # GEMINI, OPENAI, or ANTHROPIC
    error: Optional[str] = None


# ============================================================================
# Roles & Learning Resources Models
# ============================================================================

class RolesResponse(BaseModel):
    """Available job roles"""
    success: bool
    roles: List[str] = Field(default_factory=list)


class LearnLinksResponse(BaseModel):
    """Learning resources for a skill"""
    success: bool
    skill: str
    links: List[dict] = Field(default_factory=list)  # [{title, url, type}]
    error: Optional[str] = None


# ============================================================================
# Health Check
# ============================================================================

class HealthResponse(BaseModel):
    """API health status"""
    status: str = "healthy"
    version: str
    llm_providers_configured: List[str] = Field(default_factory=list)
