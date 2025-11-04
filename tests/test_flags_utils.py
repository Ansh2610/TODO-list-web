"""
Tests for backend/flags.py and backend/utils.py
Tests feature flags and utility functions
"""
import pytest
import os
from unittest.mock import patch, mock_open
from backend.flags import str_to_bool
from backend.utils import normalize_text, load_json


class TestFeatureFlags:
    """Test feature flag utilities"""
    
    def test_str_to_bool_true_values(self):
        """Test various true string values"""
        assert str_to_bool("true") is True
        assert str_to_bool("True") is True
        assert str_to_bool("TRUE") is True
        assert str_to_bool("1") is True
        assert str_to_bool("yes") is True
        assert str_to_bool("YES") is True
        assert str_to_bool("on") is True
        assert str_to_bool("ON") is True
        assert str_to_bool("enabled") is True
        assert str_to_bool("ENABLED") is True
    
    def test_str_to_bool_false_values(self):
        """Test various false string values"""
        assert str_to_bool("false") is False
        assert str_to_bool("False") is False
        assert str_to_bool("FALSE") is False
        assert str_to_bool("0") is False
        assert str_to_bool("no") is False
        assert str_to_bool("off") is False
        assert str_to_bool("disabled") is False
        assert str_to_bool("random_string") is False
    
    def test_str_to_bool_none_default_true(self):
        """Test None with default=True"""
        assert str_to_bool(None, default=True) is True
    
    def test_str_to_bool_none_default_false(self):
        """Test None with default=False"""
        assert str_to_bool(None, default=False) is False
    
    def test_str_to_bool_empty_string(self):
        """Test empty string defaults to False"""
        assert str_to_bool("") is False
    
    def test_str_to_bool_whitespace(self):
        """Test whitespace string"""
        assert str_to_bool("  ") is False


class TestTextNormalization:
    """Test text normalization utilities"""
    
    def test_normalize_text_lowercase(self):
        """Test conversion to lowercase"""
        result = normalize_text("PYTHON JavaScript")
        assert result == "python javascript"
    
    def test_normalize_text_unicode_to_ascii(self):
        """Test Unicode to ASCII conversion"""
        result = normalize_text("café résumé naïve")
        assert result == "cafe resume naive"
    
    def test_normalize_text_whitespace_collapse(self):
        """Test multiple whitespace collapse"""
        result = normalize_text("Python    JavaScript    React")
        assert result == "python javascript react"
    
    def test_normalize_text_trim(self):
        """Test leading/trailing whitespace removal"""
        result = normalize_text("  Python  ")
        assert result == "python"
    
    def test_normalize_text_newlines_and_tabs(self):
        """Test newlines and tabs converted to spaces"""
        result = normalize_text("Python\nJavaScript\tReact")
        assert result == "python javascript react"
    
    def test_normalize_text_empty_string(self):
        """Test empty string normalization"""
        result = normalize_text("")
        assert result == ""
    
    def test_normalize_text_special_chars(self):
        """Test special characters preservation"""
        result = normalize_text("C++ C# .NET")
        assert result == "c++ c# .net"


class TestJSONLoading:
    """Test JSON loading utility"""
    
    def test_load_json_dict(self):
        """Test loading JSON object"""
        mock_json = '{"key": "value", "number": 42}'
        
        with patch('builtins.open', mock_open(read_data=mock_json)):
            result = load_json("fake.json")
        
        assert result == {"key": "value", "number": 42}
    
    def test_load_json_list(self):
        """Test loading JSON array"""
        mock_json = '["Python", "JavaScript", "React"]'
        
        with patch('builtins.open', mock_open(read_data=mock_json)):
            result = load_json("fake.json")
        
        assert result == ["Python", "JavaScript", "React"]
    
    def test_load_json_nested(self):
        """Test loading nested JSON structure"""
        mock_json = '{"skills": ["Python", "Docker"], "count": 2}'
        
        with patch('builtins.open', mock_open(read_data=mock_json)):
            result = load_json("fake.json")
        
        assert result["skills"] == ["Python", "Docker"]
        assert result["count"] == 2
