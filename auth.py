"""
API Key authentication for the Product Sustainability & Impact Assessment API.
Uses header-based API key validation (X-API-Key). Key loaded from .env via python-dotenv.
"""

import os

from dotenv import load_dotenv
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

load_dotenv()

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

# Load from environment; fallback for local dev only (do not rely in production)
VALID_API_KEYS: set[str] = set()
_env_key = os.environ.get("API_KEY", "").strip()
if _env_key:
    VALID_API_KEYS.add(_env_key)
if not VALID_API_KEYS:
    # Development fallback when .env is missing or API_KEY not set
    VALID_API_KEYS.add("demo-api-key-change-in-production")


def validate_api_key(api_key: str = Security(API_KEY_HEADER)) -> str:
    """
    Validate the API key from the request header.
    Returns the key if valid; raises 401 Unauthorized otherwise.
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key. Provide X-API-Key header.",
        )
    if api_key not in VALID_API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key.",
        )
    return api_key
