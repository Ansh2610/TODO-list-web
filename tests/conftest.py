"""
Pytest configuration and fixtures for backend tests
"""
import pytest
import os
from pathlib import Path
from httpx import AsyncClient, ASGITransport
from api.main import app


@pytest.fixture
def test_data_dir():
    """Return path to test data directory"""
    return Path(__file__).parent / "test_data"


@pytest.fixture
def sample_pdf_path(test_data_dir):
    """Return path to sample PDF for testing"""
    # TODO: Create a sample PDF if needed
    return test_data_dir / "sample_resume.pdf"


@pytest.fixture
async def async_client():
    """Create async HTTP client for API testing"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client


@pytest.fixture
def sample_skills():
    """Sample extracted skills for testing"""
    return {
        "languages": ["Python", "JavaScript", "SQL"],
        "frameworks": ["FastAPI", "React", "Django"],
        "tools": ["Git", "Docker", "AWS"],
        "soft_skills": ["Communication", "Problem-solving"]
    }


@pytest.fixture
def sample_job_description():
    """Sample JD text for testing"""
    return """
    We are looking for a skilled Software Engineer with experience in:
    - Strong Python programming skills
    - Experience with FastAPI or Django frameworks
    - Knowledge of Docker and containerization
    - Excellent communication and problem-solving abilities
    - Experience with Git version control
    
    Requirements:
    - 2+ years of software development experience
    - Bachelor's degree in Computer Science or related field
    - Experience with cloud platforms (AWS preferred)
    """


@pytest.fixture
def mock_llm_response():
    """Mock LLM response for testing"""
    return {
        "recommendations": [
            "Expand your cloud platform expertise beyond AWS to include GCP and Azure",
            "Add experience with CI/CD pipelines for automated deployment",
            "Consider certifications in cloud architecture"
        ],
        "gaps": ["Limited cloud certifications", "No CI/CD experience mentioned"],
        "strengths": ["Strong Python skills", "Modern framework knowledge"]
    }
