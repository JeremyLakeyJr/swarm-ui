"""Ollama integration client.

Provides async helpers for communicating with a running Ollama instance
for chat completions, model listing, and streaming responses.
"""

from __future__ import annotations

from typing import Any, AsyncIterator

import httpx

from backend.config import get_settings


class OllamaClient:
    """Lightweight async wrapper around the Ollama HTTP API."""

    def __init__(self, base_url: str | None = None, model: str | None = None):
        settings = get_settings()
        self.base_url = (base_url or settings.ollama_base_url).rstrip("/")
        self.model = model or settings.ollama_model

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    async def list_models(self) -> list[dict[str, Any]]:
        """Return available models from the Ollama server."""
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(f"{self.base_url}/api/tags")
            resp.raise_for_status()
            return resp.json().get("models", [])

    async def chat(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
    ) -> dict[str, Any]:
        """Send a chat completion request (non-streaming)."""
        payload = {
            "model": model or self.model,
            "messages": messages,
            "stream": False,
        }
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{self.base_url}/api/chat", json=payload
            )
            resp.raise_for_status()
            return resp.json()

    async def chat_stream(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        """Yield streamed chat tokens from Ollama."""
        payload = {
            "model": model or self.model,
            "messages": messages,
            "stream": True,
        }
        async with httpx.AsyncClient(timeout=120) as client:
            async with client.stream(
                "POST", f"{self.base_url}/api/chat", json=payload
            ) as resp:
                resp.raise_for_status()
                import json as _json

                async for line in resp.aiter_lines():
                    if line.strip():
                        yield _json.loads(line)

    async def health_check(self) -> bool:
        """Return True when the Ollama server is reachable."""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                return resp.status_code == 200
        except httpx.HTTPError:
            return False
