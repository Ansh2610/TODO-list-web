"""
API Configuration and Security Settings
"""
import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """API configuration with validation"""
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore"  # Ignore extra fields from .env
    }
    
    # API Settings
    API_TITLE: str = "Resume Skill Analyzer API"
    API_VERSION: str = "1.0.0"
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000
    
    # Security Limits
    MAX_FILE_SIZE_MB: int = 5
    MAX_FILE_SIZE_BYTES: int = MAX_FILE_SIZE_MB * 1024 * 1024
    ALLOWED_MIME_TYPES: List[str] = ["application/pdf"]
    MAX_TEXT_LENGTH: int = 1800  # Privacy truncation limit
    
    # Rate Limiting (per IP)
    RATE_LIMIT_AI_CALLS: int = 5  # AI insights per session
    RATE_LIMIT_WINDOW_SECONDS: int = 3600  # 1 hour window
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:8501",  # Streamlit default
        "http://127.0.0.1:8501",
    ]
    
    # LLM Settings (from .env)
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    LLM_PROVIDERS: str = "GEMINI,OPENAI,ANTHROPIC"


settings = Settings()
