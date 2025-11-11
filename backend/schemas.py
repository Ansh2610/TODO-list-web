"""
Pydantic schemas for AI recommendations
Ensures strict validation of LLM responses
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import List


class AIRecommendations(BaseModel):
    """
    Strict schema for AI-generated career recommendations.
    
    All fields are required with length constraints to ensure
    quality output from any LLM provider.
    """
    model_config = ConfigDict(extra="ignore")  # Ignore unexpected fields
    
    coverage_explanation: str = Field(
        ..., 
        min_length=50,
        max_length=3000,
        description="4-6 detailed sentences explaining coverage with specific skill gap analysis"
    )
    
    top_missing_skills: str = Field(
        ...,
        min_length=100,
        max_length=5000,
        description="Detailed analysis of 5 top skills with learning resources and URLs (4-5 sentences per skill)"
    )
    
    learning_path: str = Field(
        ...,
        min_length=100,
        max_length=5000,
        description="6-8 sentences with detailed 6-month roadmap broken into phases with course URLs"
    )
    
    project_ideas: str = Field(
        ...,
        min_length=100,
        max_length=4000,
        description="3-4 detailed project ideas with tech stacks, complexity, and GitHub links (4-5 sentences each)"
    )
    
    resume_tweaks: str = Field(
        ...,
        min_length=50,
        max_length=3000,
        description="6-8 specific, actionable resume optimization tips with examples"
    )


def validate_ai_payload(payload: dict) -> AIRecommendations:
    """
    Validate LLM response against strict schema.
    
    Args:
        payload: Raw dict from LLM
        
    Returns:
        Validated AIRecommendations object
        
    Raises:
        ValidationError: If payload doesn't match schema
    """
    return AIRecommendations(**payload)
