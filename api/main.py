"""
FastAPI Main Application
Privacy-first API for resume skill analysis with LLM integration
"""
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from api.config import settings
from api.routers import parse, benchmark, ai, resources, export
from api.models import HealthResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup/shutdown lifecycle"""
    logger.info(f"🚀 Starting {settings.API_TITLE} v{settings.API_VERSION}")
    logger.info(f"🔒 Max file size: {settings.MAX_FILE_SIZE_MB}MB")
    logger.info(f"🤖 LLM Providers: {settings.LLM_PROVIDERS}")
    yield
    logger.info("👋 Shutting down API")


# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="Privacy-first resume skill analyzer with AI-powered career insights",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all exception handler for security"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error. Please try again later."
        }
    )


# Health check endpoint
@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Check API health and configuration"""
    configured_providers = []
    if settings.GEMINI_API_KEY:
        configured_providers.append("GEMINI")
    if settings.OPENAI_API_KEY:
        configured_providers.append("OPENAI")
    if settings.ANTHROPIC_API_KEY:
        configured_providers.append("ANTHROPIC")
    
    return HealthResponse(
        status="healthy",
        version=settings.API_VERSION,
        llm_providers_configured=configured_providers
    )


# Include routers
app.include_router(parse.router, prefix="/api", tags=["Parse"])
app.include_router(benchmark.router, prefix="/api", tags=["Benchmark"])
app.include_router(ai.router, prefix="/api", tags=["AI Insights"])
app.include_router(resources.router, prefix="/api", tags=["Resources"])
app.include_router(export.router, prefix="/api", tags=["Export"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True,
        log_level="info"
    )
