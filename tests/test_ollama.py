"""Tests for the Ollama integration client."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from backend.integrations.ollama_client import OllamaClient


@pytest.fixture
def client():
    return OllamaClient(base_url="http://test-ollama:11434", model="testmodel")


class TestOllamaClient:
    """Unit tests for OllamaClient."""

    @pytest.mark.asyncio
    async def test_list_models(self, client):
        mock_resp = httpx.Response(
            200,
            json={"models": [{"name": "testmodel"}]},
            request=httpx.Request("GET", "http://test-ollama:11434/api/tags"),
        )
        with patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_resp):
            models = await client.list_models()
        assert len(models) == 1
        assert models[0]["name"] == "testmodel"

    @pytest.mark.asyncio
    async def test_chat(self, client):
        mock_resp = httpx.Response(
            200,
            json={
                "model": "testmodel",
                "message": {"role": "assistant", "content": "Hello!"},
            },
            request=httpx.Request("POST", "http://test-ollama:11434/api/chat"),
        )
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_resp):
            result = await client.chat([{"role": "user", "content": "Hi"}])
        assert result["message"]["content"] == "Hello!"

    @pytest.mark.asyncio
    async def test_health_check_ok(self, client):
        mock_resp = httpx.Response(
            200,
            json={"models": []},
            request=httpx.Request("GET", "http://test-ollama:11434/api/tags"),
        )
        with patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_resp):
            assert await client.health_check() is True

    @pytest.mark.asyncio
    async def test_health_check_fail(self, client):
        with patch(
            "httpx.AsyncClient.get",
            new_callable=AsyncMock,
            side_effect=httpx.ConnectError("nope"),
        ):
            assert await client.health_check() is False
