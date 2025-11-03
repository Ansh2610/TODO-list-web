"""
API Client for Streamlit Frontend
Handles all communication with FastAPI backend
"""
import logging
from typing import List, Optional, Dict, Any
import httpx
from pathlib import Path

logger = logging.getLogger(__name__)


class APIClient:
    """Client for Resume Skill Analyzer API"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        """
        Initialize API client
        
        Args:
            base_url: FastAPI server URL
        """
        self.base_url = base_url
        self.timeout = 30.0  # 30 second timeout for API calls
        
    def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make HTTP request to API with error handling
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments for httpx request
            
        Returns:
            JSON response as dict
            
        Raises:
            httpx.HTTPError: On network or HTTP errors
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.request(method, url, **kwargs)
                response.raise_for_status()
                return response.json()
                
        except httpx.TimeoutException:
            logger.error(f"Request timeout: {method} {endpoint}")
            raise
        except httpx.HTTPError as e:
            logger.error(f"HTTP error: {e}")
            raise
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check API health and configuration
        
        Returns:
            Health status with version and configured providers
        """
        return self._make_request("GET", "/health")
    
    def parse_resume(self, pdf_file_path: str) -> Dict[str, Any]:
        """
        Upload and parse PDF resume
        
        Args:
            pdf_file_path: Path to PDF file
            
        Returns:
            {
                "success": bool,
                "skills": List[str],
                "skill_count": int,
                "text_preview": str,
                "error": Optional[str]
            }
        """
        pdf_path = Path(pdf_file_path)
        
        with open(pdf_path, "rb") as f:
            files = {"file": (pdf_path.name, f, "application/pdf")}
            return self._make_request("POST", "/api/parse", files=files)
    
    def benchmark_skills(
        self,
        resume_skills: List[str],
        target_role: Optional[str] = None,
        target_skills: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Benchmark skills against target role or custom JD
        
        Args:
            resume_skills: Skills extracted from resume
            target_role: Predefined role (e.g., "Software Engineer")
            target_skills: Custom JD skills (alternative to target_role)
            
        Returns:
            {
                "success": bool,
                "coverage_percentage": float,
                "found_skills": List[str],
                "missing_skills": List[str],
                "target_role": Optional[str],
                "error": Optional[str]
            }
        """
        payload = {
            "resume_skills": resume_skills,
            "target_role": target_role,
            "target_skills": target_skills
        }
        return self._make_request("POST", "/api/benchmark", json=payload)
    
    def get_ai_insights(
        self,
        found_skills: List[str],
        missing_skills: List[str],
        target_role: str,
        coverage_percentage: float
    ) -> Dict[str, Any]:
        """
        Get AI-powered career insights
        
        Args:
            found_skills: Matched skills
            missing_skills: Gap analysis
            target_role: Job role context
            coverage_percentage: Current coverage
            
        Returns:
            {
                "success": bool,
                "coverage_explanation": str,
                "top_missing_skills": str,
                "learning_path": str,
                "project_ideas": str,
                "resume_tweaks": str,
                "provider_used": Optional[str],
                "error": Optional[str]
            }
        """
        payload = {
            "found_skills": found_skills,
            "missing_skills": missing_skills,
            "target_role": target_role,
            "coverage_percentage": coverage_percentage
        }
        return self._make_request("POST", "/api/ai", json=payload)
    
    def get_roles(self) -> Dict[str, Any]:
        """
        Get available job roles
        
        Returns:
            {
                "success": bool,
                "roles": List[str]
            }
        """
        return self._make_request("GET", "/api/roles")
    
    def get_learning_links(self, skill: str) -> Dict[str, Any]:
        """
        Get learning resources for a skill
        
        Args:
            skill: Skill name
            
        Returns:
            {
                "success": bool,
                "skill": str,
                "links": List[Dict],
                "error": Optional[str]
            }
        """
        return self._make_request("GET", f"/api/learn-links/{skill}")


# Singleton instance
_client = None


def get_api_client(base_url: str = "http://127.0.0.1:8000") -> APIClient:
    """
    Get or create API client singleton
    
    Args:
        base_url: FastAPI server URL
        
    Returns:
        APIClient instance
    """
    global _client
    if _client is None:
        _client = APIClient(base_url)
    return _client
