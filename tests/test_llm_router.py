"""
Unit tests for LLM router and AI recommendations
Tests with mocked API calls - no real LLM calls
"""
import pytest
from unittest.mock import patch, MagicMock
from backend.llm_router import LLMRouter
from backend.benchmark import get_ai_recommendations


class TestLLMRouter:
    """Test LLM router with mocked providers"""
    
    def test_router_initialization(self):
        """Test LLMRouter initializes correctly"""
        router = LLMRouter()
        assert router.providers is not None
        assert router.timeout > 0
        assert router.max_tokens > 0
        assert isinstance(router.keys, dict)
    
    def test_clean_response(self):
        """Test response cleaning removes code fences"""
        router = LLMRouter()
        
        # Test with code fences
        cleaned = router._clean_response("```json\n{\"test\": \"data\"}\n```")
        assert cleaned == "{\"test\": \"data\"}"
        
        # Test with JSON prefix
        cleaned = router._clean_response("json\n{\"key\": \"value\"}")
        assert cleaned == "{\"key\": \"value\"}"


class TestAIRecommendations:
    """Test AI recommendation generation"""
    
    @patch.object(LLMRouter, 'call')
    def test_get_ai_recommendations_success(self, mock_call):
        """Test successful AI recommendation generation"""
        # Mock valid LLM response
        mock_call.return_value = {
            "coverage_explanation": "You have 60% of required skills. Strong Python foundation.",
            "top_missing_skills": "Docker, AWS, Kubernetes",
            "learning_path": "Month 1: Docker basics, Month 2: AWS fundamentals, Month 3: K8s",
            "project_ideas": "Build a containerized microservice, deploy to AWS ECS",
            "resume_tweaks": "Add Docker and AWS keywords to summary section"
        }
        
        result = get_ai_recommendations(
            extracted_skills=["Python", "FastAPI", "Git"],
            missing_skills=["Docker", "AWS", "Kubernetes"],
            role_name="Backend Developer",
            coverage_pct=60.0
        )
        
        assert result is not None
        # Result is a Pydantic model (AIRecommendations), access as attributes
        assert hasattr(result, 'coverage_explanation')
        assert hasattr(result, 'top_missing_skills')
        assert "Docker" in result.top_missing_skills
    
    @patch.object(LLMRouter, 'call')
    def test_get_ai_recommendations_fallback(self, mock_call):
        """Test deterministic fallback when LLM fails"""
        # Mock LLM failure (all providers down)
        mock_call.side_effect = RuntimeError("All LLM providers failed")
        
        result = get_ai_recommendations(
            extracted_skills=["Python", "Flask"],
            missing_skills=["Docker", "AWS", "Kubernetes"],
            role_name="DevOps Engineer",
            coverage_pct=40.0
        )
        
        # Should return deterministic fallback (Pydantic model, not None)
        assert result is not None
        # Result is AIRecommendations model
        assert hasattr(result, 'coverage_explanation')
        assert hasattr(result, 'top_missing_skills')
        # Fallback should mention missing skills
        assert any(skill in result.top_missing_skills for skill in ["Docker", "AWS", "Kubernetes"])
    
    def test_get_ai_recommendations_empty_skills(self):
        """Test with empty skill lists"""
        # This should use fallback since no skills to analyze
        result = get_ai_recommendations(
            extracted_skills=[],
            missing_skills=[],
            role_name="Software Engineer",
            coverage_pct=0.0
        )
        
        # Fallback returns Pydantic model or None
        assert result is None or hasattr(result, 'coverage_explanation')
