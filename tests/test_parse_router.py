"""
Tests for api/routers/parse.py
Tests PDF upload endpoint with security validation
"""
import pytest
from fastapi import UploadFile
from httpx import AsyncClient, ASGITransport
from io import BytesIO
from unittest.mock import Mock, patch, AsyncMock

from api.main import app
from api.routers.parse import validate_pdf_upload, extract_text_from_pdf


@pytest.fixture
def valid_pdf_bytes():
    """Create mock PDF bytes with valid header"""
    # Valid PDF starts with %PDF
    return b'%PDF-1.4\n' + b'A' * 1000


@pytest.fixture
def invalid_pdf_bytes():
    """Create invalid PDF bytes (wrong magic bytes)"""
    return b'NOT A PDF' + b'A' * 1000


class TestValidatePDFUpload:
    """Test PDF upload validation"""
    
    @pytest.mark.asyncio
    async def test_validate_pdf_valid(self, valid_pdf_bytes):
        """Test valid PDF passes validation"""
        mock_file = AsyncMock(spec=UploadFile)
        mock_file.content_type = "application/pdf"
        mock_file.read = AsyncMock(return_value=valid_pdf_bytes)
        
        result = await validate_pdf_upload(mock_file)
        assert result == valid_pdf_bytes
    
    @pytest.mark.asyncio
    async def test_validate_pdf_invalid_mime(self, valid_pdf_bytes):
        """Test invalid MIME type raises exception"""
        mock_file = AsyncMock(spec=UploadFile)
        mock_file.content_type = "application/msword"
        mock_file.read = AsyncMock(return_value=valid_pdf_bytes)
        
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await validate_pdf_upload(mock_file)
        assert exc_info.value.status_code == 400
        assert "Invalid file type" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_validate_pdf_too_large(self):
        """Test file over 5MB raises exception"""
        # Create 6MB file
        large_pdf = b'%PDF-1.4\n' + b'A' * (6 * 1024 * 1024)
        
        mock_file = AsyncMock(spec=UploadFile)
        mock_file.content_type = "application/pdf"
        mock_file.read = AsyncMock(return_value=large_pdf)
        
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await validate_pdf_upload(mock_file)
        assert exc_info.value.status_code == 413
        assert "File too large" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_validate_pdf_invalid_magic_bytes(self, invalid_pdf_bytes):
        """Test invalid PDF header raises exception"""
        mock_file = AsyncMock(spec=UploadFile)
        mock_file.content_type = "application/pdf"
        mock_file.read = AsyncMock(return_value=invalid_pdf_bytes)
        
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await validate_pdf_upload(mock_file)
        assert exc_info.value.status_code == 400
        assert "does not have valid PDF header" in exc_info.value.detail


class TestExtractTextFromPDF:
    """Test PDF text extraction in parse router"""
    
    def test_extract_text_success(self):
        """Test successful text extraction"""
        # Mock pdfplumber
        mock_page = Mock()
        mock_page.extract_text.return_value = "Python JavaScript React"
        
        mock_pdf = Mock()
        mock_pdf.__enter__ = Mock(return_value=mock_pdf)
        mock_pdf.__exit__ = Mock(return_value=None)
        mock_pdf.pages = [mock_page]
        
        with patch('pdfplumber.open', return_value=mock_pdf):
            result = extract_text_from_pdf(b'%PDF-1.4\nfake content')
        
        assert "Python" in result
        assert "JavaScript" in result
    
    def test_extract_text_multiple_pages(self):
        """Test multi-page extraction"""
        mock_page1 = Mock()
        mock_page1.extract_text.return_value = "Page 1"
        
        mock_page2 = Mock()
        mock_page2.extract_text.return_value = "Page 2"
        
        mock_pdf = Mock()
        mock_pdf.__enter__ = Mock(return_value=mock_pdf)
        mock_pdf.__exit__ = Mock(return_value=None)
        mock_pdf.pages = [mock_page1, mock_page2]
        
        with patch('pdfplumber.open', return_value=mock_pdf):
            result = extract_text_from_pdf(b'fake_pdf')
        
        assert "Page 1" in result
        assert "Page 2" in result
    
    def test_extract_text_failure(self):
        """Test extraction failure raises ValueError"""
        with patch('pdfplumber.open', side_effect=Exception("Corrupted PDF")):
            with pytest.raises(ValueError, match="Failed to extract text from PDF"):
                extract_text_from_pdf(b'corrupted')


class TestParseEndpoint:
    """Test /parse endpoint integration"""
    
    @pytest.mark.asyncio
    async def test_parse_endpoint_success(self):
        """Test successful PDF parse"""
        # Mock valid PDF file
        pdf_content = b'%PDF-1.4\nSoftware Engineer with Python and JavaScript skills'
        
        # Mock pdfplumber extraction
        mock_page = Mock()
        mock_page.extract_text.return_value = "Software Engineer with Python and JavaScript skills"
        
        mock_pdf = Mock()
        mock_pdf.__enter__ = Mock(return_value=mock_pdf)
        mock_pdf.__exit__ = Mock(return_value=None)
        mock_pdf.pages = [mock_page]
        
        with patch('pdfplumber.open', return_value=mock_pdf):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                files = {"file": ("resume.pdf", pdf_content, "application/pdf")}
                response = await client.post("/api/parse", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "skills" in data
        assert isinstance(data["skills"], list)
        assert "text_preview" in data
    
    @pytest.mark.asyncio
    async def test_parse_endpoint_invalid_mime(self):
        """Test invalid MIME type rejection"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            files = {"file": ("resume.docx", b"fake content", "application/msword")}
            response = await client.post("/api/parse", files=files)
        
        assert response.status_code == 400
        assert "Invalid file type" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_parse_endpoint_file_too_large(self):
        """Test file size limit"""
        # Create 6MB file with valid PDF header
        large_file = b'%PDF-1.4\n' + b'A' * (6 * 1024 * 1024)
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            files = {"file": ("large.pdf", large_file, "application/pdf")}
            response = await client.post("/api/parse", files=files)
        
        assert response.status_code == 413
        assert "File too large" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_parse_endpoint_invalid_pdf_header(self):
        """Test invalid PDF magic bytes"""
        invalid_pdf = b'NOT A PDF'
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            files = {"file": ("fake.pdf", invalid_pdf, "application/pdf")}
            response = await client.post("/api/parse", files=files)
        
        assert response.status_code == 400
        assert "does not have valid PDF header" in response.json()["detail"]
