"""
Unit tests for JD parser module (backend/jd_parser.py)
"""
import pytest
from backend.jd_parser import parse_jd_skills, validate_jd_text
from backend.utils import load_json


@pytest.fixture
def skill_bank():
    """Load skill bank for testing"""
    return load_json("data/skill_bank.json")


@pytest.fixture
def sample_jd():
    """Sample valid job description"""
    return """
    Senior Backend Developer Position
    
    We are looking for an experienced Backend Developer to join our team.
    
    Required Skills:
    - Strong Python programming skills (5+ years)
    - Experience with FastAPI or Django frameworks
    - Database knowledge: PostgreSQL, Redis
    - Cloud platforms: AWS (EC2, S3, Lambda)
    - Containerization: Docker, Kubernetes
    - Version control: Git
    - CI/CD pipelines
    
    Nice to have:
    - GraphQL experience
    - Microservices architecture
    - Message queues (RabbitMQ, Kafka)
    
    Responsibilities:
    - Design and build scalable backend services
    - Write clean, maintainable code
    - Collaborate with frontend team
    - Mentor junior developers
    """


class TestJDValidation:
    """Test job description validation"""
    
    def test_validate_jd_text_valid(self, sample_jd):
        """Test validation with valid JD"""
        is_valid, error = validate_jd_text(sample_jd)
        assert is_valid is True
        # Error can be empty string or None
        assert not error  # Falsy check works for both
    
    def test_validate_jd_text_too_short(self):
        """Test validation fails for short text"""
        short_text = "Python developer needed"
        is_valid, error = validate_jd_text(short_text)
        assert is_valid is False
        assert error is not None
        assert "too short" in error.lower() or "minimum" in error.lower()
    
    def test_validate_jd_text_empty(self):
        """Test validation fails for empty text"""
        is_valid, error = validate_jd_text("")
        assert is_valid is False
        assert error is not None


class TestJDSkillExtraction:
    """Test skill extraction from job descriptions"""
    
    def test_parse_jd_skills_basic(self, sample_jd, skill_bank):
        """Test basic JD skill extraction"""
        skills = parse_jd_skills(sample_jd, skill_bank)
        
        assert isinstance(skills, list)
        assert len(skills) > 0
        # Should extract Python from the JD
        skill_lower = [s.lower() for s in skills]
        assert "python" in skill_lower
    
    def test_parse_jd_skills_empty(self, skill_bank):
        """Test parsing empty JD raises error"""
        with pytest.raises(ValueError):
            parse_jd_skills("", skill_bank)
    
    def test_parse_jd_skills_too_short(self, skill_bank):
        """Test parsing short JD raises error"""
        short_jd = "Need Python dev"
        with pytest.raises(ValueError):
            parse_jd_skills(short_jd, skill_bank)
    
    def test_parse_jd_skills_unique(self, sample_jd, skill_bank):
        """Test that returned skills are unique"""
        skills = parse_jd_skills(sample_jd, skill_bank)
        
        # Should not have duplicates
        assert len(skills) == len(set(skills))
    
    def test_parse_jd_skills_requirements_section(self, skill_bank):
        """Test extraction from requirements section"""
        jd = """
        Requirements for Software Engineer Role:
        - Python programming experience
        - FastAPI web framework knowledge
        - Docker containerization skills
        - AWS cloud platform experience
        - Git version control
        
        We are building next-generation cloud applications using modern
        technologies. Join our team of experienced engineers working on
        exciting projects with cutting-edge tools and frameworks.
        """ * 2  # Duplicate to meet min length
        
        skills = parse_jd_skills(jd, skill_bank)
        
        assert len(skills) > 0
        skill_lower = [s.lower() for s in skills]
        assert "python" in skill_lower


class TestJDEdgeCases:
    """Test edge cases in JD parsing"""
    
    def test_jd_with_special_characters(self, skill_bank):
        """Test JD with special characters"""
        jd = """
        Looking for developer with Python/JavaScript knowledge.
        Experience with AWS & Docker required.
        Must know Git + CI/CD pipelines and modern development practices.
        Strong understanding of software engineering principles needed.
        Work with cross-functional teams to deliver high-quality solutions.
        """ * 3  # Repeat to meet min length
        
        skills = parse_jd_skills(jd, skill_bank)
        assert isinstance(skills, list)
        assert len(skills) > 0
    
    def test_jd_with_numbers(self, skill_bank):
        """Test JD with version numbers"""
        jd = """
        Requirements:
        - Python 3.11+ experience required
        - Node.js v18 or higher
        - AWS services including EC2, S3, RDS
        - Docker containerization and Kubernetes orchestration
        - 5+ years of software development experience
        - Bachelor's degree in Computer Science or related field
        """ * 3  # Repeat to meet min length
        
        skills = parse_jd_skills(jd, skill_bank)
        # Should extract skills even with version numbers
        assert len(skills) > 0
