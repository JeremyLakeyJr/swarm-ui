"""Authentication and security utilities.

Provides JWT-based token creation / verification and an API-key
dependency for protecting endpoints.
"""

from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.config import Settings, get_settings

_bearer_scheme = HTTPBearer(auto_error=False)


# ------------------------------------------------------------------
# Token helpers
# ------------------------------------------------------------------


def _get_jose():
    """Lazily import python-jose so the module can load without it."""
    try:
        from jose import JWTError, jwt
        return jwt, JWTError
    except ImportError:
        return None, None


def create_access_token(
    data: dict[str, Any],
    settings: Settings | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a signed JWT access token."""
    jwt, _ = _get_jose()
    if jwt is None:
        raise RuntimeError("python-jose is required for JWT support")
    settings = settings or get_settings()
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(hours=8))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.app_secret_key, algorithm="HS256")


def verify_token(token: str, settings: Settings | None = None) -> dict[str, Any]:
    """Decode and verify a JWT token; raises on failure."""
    jwt, JWTError = _get_jose()
    if jwt is None:
        raise RuntimeError("python-jose is required for JWT support")
    settings = settings or get_settings()
    try:
        return jwt.decode(token, settings.app_secret_key, algorithms=["HS256"])
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc


# ------------------------------------------------------------------
# FastAPI dependencies
# ------------------------------------------------------------------


async def require_auth(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    settings: Settings = Depends(get_settings),
) -> dict[str, Any]:
    """Dependency that enforces a valid Bearer token.

    When ``APP_SECRET_KEY`` is still the default placeholder the check
    is skipped so local development works without tokens.
    """
    if settings.app_secret_key == "change-me-to-a-random-secret":
        # Development mode – no auth required
        return {"sub": "dev"}

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
        )
    return verify_token(credentials.credentials, settings)


def generate_api_key() -> str:
    """Generate a secure random API key string."""
    return secrets.token_urlsafe(32)
