"""
Tests for backend/security.py
Tests file validation, size limits, and security functions
"""
from backend.security import (
    allowed_file,
    validate_file_size,
    secure_hash_name,
    truncate_text,
    MAX_FILE_MB,
    MAX_TEXT_CHARS
)


class TestFileValidation:
    """Test file validation functions"""
    
    def test_allowed_file_valid_pdf(self):
        """Test valid PDF file passes validation"""
        assert allowed_file("resume.pdf", "application/pdf") is True
    
    def test_allowed_file_uppercase_extension(self):
        """Test uppercase .PDF extension"""
        assert allowed_file("Resume.PDF", "application/pdf") is True
    
    def test_allowed_file_invalid_extension(self):
        """Test non-PDF extension fails"""
        assert allowed_file("resume.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document") is False
    
    def test_allowed_file_invalid_mime(self):
        """Test invalid MIME type fails"""
        assert allowed_file("resume.pdf", "application/msword") is False
    
    def test_allowed_file_none_mime_with_pdf_extension(self):
        """Test None MIME type with .pdf extension (fallback)"""
        assert allowed_file("resume.pdf", None) is True
    
    def test_allowed_file_none_mime_without_pdf_extension(self):
        """Test None MIME type without .pdf extension fails"""
        assert allowed_file("resume.docx", None) is False


class TestFileSizeValidation:
    """Test file size validation"""
    
    def test_validate_file_size_under_limit(self):
        """Test file under 5MB passes"""
        small_file = b"A" * (1 * 1024 * 1024)  # 1MB
        assert validate_file_size(small_file) is True
    
    def test_validate_file_size_at_limit(self):
        """Test file exactly at 5MB limit"""
        exact_file = b"A" * (MAX_FILE_MB * 1024 * 1024)
        assert validate_file_size(exact_file) is True
    
    def test_validate_file_size_over_limit(self):
        """Test file over 5MB fails"""
        large_file = b"A" * (MAX_FILE_MB * 1024 * 1024 + 1)
        assert validate_file_size(large_file) is False
    
    def test_validate_file_size_empty(self):
        """Test empty file passes"""
        assert validate_file_size(b"") is True


class TestSecureHashName:
    """Test filename hashing"""
    
    def test_secure_hash_name_consistent(self):
        """Test same filename produces same hash"""
        hash1 = secure_hash_name("resume.pdf")
        hash2 = secure_hash_name("resume.pdf")
        assert hash1 == hash2
    
    def test_secure_hash_name_different(self):
        """Test different filenames produce different hashes"""
        hash1 = secure_hash_name("resume1.pdf")
        hash2 = secure_hash_name("resume2.pdf")
        assert hash1 != hash2
    
    def test_secure_hash_name_length(self):
        """Test hash is 16 characters"""
        hash_name = secure_hash_name("resume.pdf")
        assert len(hash_name) == 16
    
    def test_secure_hash_name_no_special_chars(self):
        """Test hash contains only alphanumeric chars"""
        hash_name = secure_hash_name("resume with spaces.pdf")
        assert hash_name.isalnum()


class TestTextTruncation:
    """Test text truncation"""
    
    def test_truncate_text_under_limit(self):
        """Test text under limit is not truncated"""
        short_text = "A" * 1000
        result = truncate_text(short_text)
        assert result == short_text
        assert len(result) == 1000
    
    def test_truncate_text_at_limit(self):
        """Test text exactly at limit"""
        exact_text = "A" * MAX_TEXT_CHARS
        result = truncate_text(exact_text)
        assert result == exact_text
        assert len(result) == MAX_TEXT_CHARS
    
    def test_truncate_text_over_limit(self):
        """Test text over limit gets truncated"""
        long_text = "A" * (MAX_TEXT_CHARS + 10000)
        result = truncate_text(long_text)
        assert len(result) == MAX_TEXT_CHARS
        assert result == long_text[:MAX_TEXT_CHARS]
    
    def test_truncate_text_empty(self):
        """Test empty text"""
        result = truncate_text("")
        assert result == ""
    
    def test_truncate_text_unicode(self):
        """Test Unicode characters are handled correctly"""
        unicode_text = "日本語" * 50000  # Japanese characters
        result = truncate_text(unicode_text)
        assert len(result) <= MAX_TEXT_CHARS
