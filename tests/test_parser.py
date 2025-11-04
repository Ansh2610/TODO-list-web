"""
Tests for backend/parser.py
Tests PDF text extraction functionality
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from backend.parser import extract_text_from_pdf


class TestPDFExtraction:
    """Test PDF text extraction"""
    
    def test_extract_text_single_page(self):
        """Test extracting text from single-page PDF"""
        # Mock pdfplumber
        mock_page = Mock()
        mock_page.extract_text.return_value = "Python skills\nJavaScript\nReact"
        
        mock_pdf = Mock()
        mock_pdf.__enter__ = Mock(return_value=mock_pdf)
        mock_pdf.__exit__ = Mock(return_value=None)
        mock_pdf.pages = [mock_page]
        
        with patch('pdfplumber.open', return_value=mock_pdf):
            result = extract_text_from_pdf(b'fake_pdf_bytes')
            
        assert "Python" in result
        assert "JavaScript" in result
        assert "React" in result
    
    def test_extract_text_multiple_pages(self):
        """Test extracting text from multi-page PDF"""
        # Mock multiple pages
        mock_page1 = Mock()
        mock_page1.extract_text.return_value = "Page 1: Python"
        
        mock_page2 = Mock()
        mock_page2.extract_text.return_value = "Page 2: JavaScript"
        
        mock_pdf = Mock()
        mock_pdf.__enter__ = Mock(return_value=mock_pdf)
        mock_pdf.__exit__ = Mock(return_value=None)
        mock_pdf.pages = [mock_page1, mock_page2]
        
        with patch('pdfplumber.open', return_value=mock_pdf):
            result = extract_text_from_pdf(b'fake_pdf_bytes')
        
        assert "Page 1: Python" in result
        assert "Page 2: JavaScript" in result
        assert "\n" in result  # Pages joined with newline
    
    def test_extract_text_empty_page(self):
        """Test handling empty pages (None return)"""
        mock_page = Mock()
        mock_page.extract_text.return_value = None
        
        mock_pdf = Mock()
        mock_pdf.__enter__ = Mock(return_value=mock_pdf)
        mock_pdf.__exit__ = Mock(return_value=None)
        mock_pdf.pages = [mock_page]
        
        with patch('pdfplumber.open', return_value=mock_pdf):
            result = extract_text_from_pdf(b'fake_pdf_bytes')
        
        # Should handle None gracefully
        assert result == ""
    
    def test_extract_text_truncation(self):
        """Test that excessively long text gets truncated"""
        # Create very long text (over 100k chars)
        long_text = "A" * 150_000
        
        mock_page = Mock()
        mock_page.extract_text.return_value = long_text
        
        mock_pdf = Mock()
        mock_pdf.__enter__ = Mock(return_value=mock_pdf)
        mock_pdf.__exit__ = Mock(return_value=None)
        mock_pdf.pages = [mock_page]
        
        with patch('pdfplumber.open', return_value=mock_pdf):
            result = extract_text_from_pdf(b'fake_pdf_bytes')
        
        # Should be truncated to 100k chars
        assert len(result) == 100_000
    
    def test_extract_text_corrupted_pdf(self):
        """Test handling corrupted PDF"""
        with patch('pdfplumber.open', side_effect=Exception("PDF is corrupted")):
            with pytest.raises(Exception, match="PDF is corrupted"):
                extract_text_from_pdf(b'corrupted_pdf')
