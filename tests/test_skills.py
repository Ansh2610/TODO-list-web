"""
Unit tests for skill extraction module (backend/skills.py)
"""
import pytest
from backend.skills import extract_skills, coverage_against_role, flatten_categories
from backend.utils import load_json


class TestSkillExtraction:
    """Test skill extraction from text"""
    
    def test_extract_skills_basic(self):
        """Test basic skill extraction"""
        text = "I have experience with Python, JavaScript, and React framework"
        skill_bank = load_json("data/skill_bank.json")
        
        result = extract_skills(text, skill_bank)
        
        assert isinstance(result, dict)
        # Should have categorized skills
        assert len(result) > 0
    
    def test_extract_skills_case_insensitive(self):
        """Test that extraction is case-insensitive"""
        text = "Skilled in PYTHON, javascript, and docker"
        skill_bank = load_json("data/skill_bank.json")
        
        result = extract_skills(text, skill_bank)
        
        # Should find skills regardless of case
        assert isinstance(result, dict)
        total_skills = sum(len(v) for v in result.values())
        assert total_skills > 0
    
    def test_extract_skills_empty_text(self):
        """Test extraction from empty text"""
        skill_bank = load_json("data/skill_bank.json")
        result = extract_skills("", skill_bank)
        
        # Should return dict with empty lists
        assert isinstance(result, dict)
        total_skills = sum(len(v) for v in result.values())
        assert total_skills == 0
    
    def test_extract_skills_no_matches(self):
        """Test extraction when no skills match"""
        text = "I like cooking and hiking on weekends with my family"
        skill_bank = load_json("data/skill_bank.json")
        
        result = extract_skills(text, skill_bank)
        
        # Should return empty categories
        total_skills = sum(len(v) for v in result.values())
        assert total_skills == 0


class TestFlattenCategories:
    """Test skill flattening"""
    
    def test_flatten_categories(self):
        """Test converting categorized dict to flat list"""
        categorized = {
            "languages": ["Python", "JavaScript"],
            "frameworks": ["React", "FastAPI"],
            "tools": ["Git", "Docker"]
        }
        
        result = flatten_categories(categorized)
        
        assert isinstance(result, list)
        assert len(result) == 6
        assert "Python" in result
        assert "Docker" in result
    
    def test_flatten_empty(self):
        """Test flattening empty dict"""
        result = flatten_categories({})
        assert result == []


class TestCoverageCalculation:
    """Test coverage calculation against roles"""
    
    def test_coverage_against_role_basic(self):
        """Test basic coverage calculation with explainable match"""
        extracted = ["Python", "FastAPI", "Docker", "Git"]
        required = ["Python", "FastAPI", "Docker", "PostgreSQL", "AWS"]
        
        result = coverage_against_role(extracted, required)
        
        assert isinstance(result, dict)
        assert "coverage_percentage" in result
        assert "matched_skills" in result
        assert "missing_skills" in result
        assert "suggestions" in result
        assert "explanation" in result
        assert 0 <= result["coverage_percentage"] <= 100
    
    def test_coverage_perfect_match(self):
        """Test coverage when all skills match"""
        skills = ["Python", "FastAPI", "Docker", "Git"]
        
        result = coverage_against_role(skills, skills)
        
        # Should be 100%
        assert result["coverage_percentage"] == 100
        assert len(result["missing_skills"]) == 0
    
    def test_coverage_no_match(self):
        """Test coverage when no skills match"""
        extracted = ["Cooking", "Gardening"]
        required = ["Python", "Docker", "AWS"]
        
        result = coverage_against_role(extracted, required)
        
        assert result["coverage_percentage"] == 0
        assert len(result["matched_skills"]) == 0
        assert len(result["missing_skills"]) == 3
    
    def test_coverage_partial_match(self):
        """Test coverage with partial skill match"""
        extracted = ["Python", "Git"]
        required = ["Python", "FastAPI", "Docker", "AWS", "Git"]
        
        result = coverage_against_role(extracted, required)
        
        # Should be between 0 and 100
        assert 0 < result["coverage_percentage"] < 100
        assert len(result["matched_skills"]) == 2
        assert len(result["missing_skills"]) == 3
    
    def test_explainable_suggestions(self):
        """Test that suggestions show % boost"""
        extracted = ["Python"]
        required = ["Python", "Docker", "AWS", "Kubernetes"]
        
        result = coverage_against_role(extracted, required)
        
        # Should have suggestions dict
        assert isinstance(result["suggestions"], dict)
        # Suggestions should show boost percentage
        if result["suggestions"]:
            # Each missing skill should have a boost value
            for skill, boost in result["suggestions"].items():
                assert isinstance(boost, int)
                assert boost > 0
