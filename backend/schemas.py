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
        min_length=10,
        max_length=500,
        description="2-3 sentences explaining why this coverage % happened (focus on skill gaps)"
    )
    
    top_missing_skills: str = Field(
        ...,
        min_length=10,
        max_length=300,
        description="1-2 sentences prioritizing 3-5 high-impact missing skills"
    )
    
    learning_path: str = Field(
        ...,
        min_length=10,
        max_length=600,
        description="3-4 sentences with concrete 3-month learning roadmap and resources"
    )
    
    project_ideas: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="2-3 sentences with 2-3 portfolio project suggestions"
    )
    
    resume_tweaks: str = Field(
        ...,
        min_length=10,
        max_length=400,
        description="2-3 sentences with tactical advice on highlighting existing skills"
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
