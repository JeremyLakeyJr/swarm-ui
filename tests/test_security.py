"""Tests for the security module."""

from __future__ import annotations

import pytest

from backend.auth.security import (
    create_access_token,
    verify_token,
    generate_api_key,
)
from backend.config import Settings


@pytest.fixture
def settings():
    return Settings(app_secret_key="test-secret-key-for-unit-tests")


class TestSecurity:
    def test_create_and_verify_token(self, settings):
        token = create_access_token({"sub": "user1"}, settings=settings)
        payload = verify_token(token, settings=settings)
        assert payload["sub"] == "user1"

    def test_verify_bad_token(self, settings):
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            verify_token("bad.token.value", settings=settings)
        assert exc_info.value.status_code == 401

    def test_generate_api_key(self):
        key = generate_api_key()
        assert len(key) > 20  # urlsafe b64 of 32 bytes
        assert isinstance(key, str)
