"""
Feature Flags
Centralized feature toggles from environment variables
"""
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def str_to_bool(value: Optional[str], default: bool = False) -> bool:
    """Convert string environment variable to boolean."""
    if value is None:
        return default
    return value.lower() in ('true', '1', 'yes', 'on', 'enabled')


# Feature Flags (read once at module import)
ENABLE_EXPORT_REPORT = str_to_bool(os.getenv("ENABLE_EXPORT_REPORT"), default=True)
ANON_COUNTER_ENABLE = str_to_bool(os.getenv("ANON_COUNTER_ENABLE"), default=False)
ENABLE_PDF_PREVIEW = str_to_bool(os.getenv("ENABLE_PDF_PREVIEW"), default=True)
DEBUG_MODE = str_to_bool(os.getenv("DEBUG_MODE"), default=False)

# Session Limits
MAX_ANALYSES_PER_SESSION = int(os.getenv("MAX_ANALYSES_PER_SESSION", "10"))
MAX_AI_RUNS_PER_SESSION = int(os.getenv("MAX_AI_RUNS_PER_SESSION", "2"))

# Log configuration on import
logger.info(f"Feature Flags Loaded:")
logger.info(f"  ENABLE_EXPORT_REPORT: {ENABLE_EXPORT_REPORT}")
logger.info(f"  ANON_COUNTER_ENABLE: {ANON_COUNTER_ENABLE}")
logger.info(f"  ENABLE_PDF_PREVIEW: {ENABLE_PDF_PREVIEW}")
logger.info(f"  MAX_ANALYSES_PER_SESSION: {MAX_ANALYSES_PER_SESSION}")
logger.info(f"  MAX_AI_RUNS_PER_SESSION: {MAX_AI_RUNS_PER_SESSION}")
logger.info(f"  DEBUG_MODE: {DEBUG_MODE}")
