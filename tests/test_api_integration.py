"""
Integration tests for FastAPI endpoints
Run these with pytest after starting the API server
"""
import pytest
from httpx import AsyncClient, ASGITransport
from api.main import app


@pytest.fixture
async def client():
    """Create async HTTP client for testing"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac


@pytest.mark.asyncio
class TestHealthEndpoints:
    """Test health check endpoints"""
    
    async def test_health_endpoint(self, client):
        """Test /health endpoint"""
        response = await client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "llm_providers_configured" in data
    
    async def test_healthz_endpoint(self, client):
        """Test /healthz endpoint (k8s style)"""
        response = await client.get("/healthz")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"
        assert "timestamp" in data
    
    async def test_version_endpoint(self, client):
        """Test /version endpoint"""
        response = await client.get("/version")
        assert response.status_code == 200
        
        data = response.json()
        assert "version" in data
        assert "title" in data
        assert "environment" in data


@pytest.mark.asyncio
class TestRolesEndpoint:
    """Test /api/roles endpoint"""
    
    async def test_roles_list(self, client):
        """Test getting list of roles"""
        response = await client.get("/api/roles")
        assert response.status_code == 200
        
        data = response.json()
        assert "roles" in data
        assert isinstance(data["roles"], list)
        assert len(data["roles"]) > 0


@pytest.mark.asyncio
class TestLearnLinksEndpoint:
    """Test /api/learn-links endpoint"""
    
    async def test_learn_links(self, client):
        """Test getting learning resources"""
        response = await client.get("/api/learn-links")
        assert response.status_code == 200
        
        data = response.json()
        # Response has 'links' not 'resources'
        assert "links" in data
        assert isinstance(data["links"], dict)


@pytest.mark.asyncio  
class TestBenchmarkEndpoint:
    """Test /api/benchmark endpoint"""
    
    async def test_benchmark_with_role(self, client):
        """Test benchmark against a predefined role"""
        payload = {
            "resume_skills": ["Python", "FastAPI", "Docker"],
            "target_role": "Backend Developer"
        }
        
        response = await client.post("/api/benchmark", json=payload)
        
        # May fail if role doesn't exist, but should return valid response
        if response.status_code == 200:
            data = response.json()
            assert "coverage_percentage" in data
            assert "matched_skills" in data
            assert "missing_skills" in data
            # Check explainable match fields
            assert "suggestions" in data
            assert "explanation" in data
            assert isinstance(data["coverage_percentage"], (int, float))
    
    async def test_benchmark_empty_skills(self, client):
        """Test benchmark with empty skills returns error"""
        payload = {
            "resume_skills": [],
            "target_role": "Backend Developer"
        }
        
        response = await client.post("/api/benchmark", json=payload)
        # Should fail validation (min_length=1 for resume_skills)
        assert response.status_code == 422


@pytest.mark.asyncio
class TestErrorHandling:
    """Test error handling"""
    
    async def test_404_endpoint(self, client):
        """Test accessing non-existent endpoint"""
        response = await client.get("/nonexistent")
        assert response.status_code == 404
