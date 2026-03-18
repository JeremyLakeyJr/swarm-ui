"""Home Assistant integration.

Communicates with a Home Assistant instance over its REST API using a
long-lived access token for authentication.
"""

from __future__ import annotations

from typing import Any

import httpx

from backend.config import get_settings


class HomeAssistantClient:
    """Async client for the Home Assistant REST API."""

    def __init__(
        self,
        url: str | None = None,
        token: str | None = None,
    ):
        settings = get_settings()
        self.url = (url or settings.homeassistant_url).rstrip("/")
        self.token = token or settings.homeassistant_token

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    async def health_check(self) -> bool:
        """Return True when the Home Assistant API is reachable."""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    f"{self.url}/api/", headers=self._headers()
                )
                return resp.status_code == 200
        except httpx.HTTPError:
            return False

    async def get_states(self) -> list[dict[str, Any]]:
        """Fetch all entity states."""
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                f"{self.url}/api/states", headers=self._headers()
            )
            resp.raise_for_status()
            return resp.json()

    async def get_entity_state(self, entity_id: str) -> dict[str, Any]:
        """Return the state of a single entity."""
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                f"{self.url}/api/states/{entity_id}",
                headers=self._headers(),
            )
            resp.raise_for_status()
            return resp.json()

    async def call_service(
        self,
        domain: str,
        service: str,
        entity_id: str | None = None,
        data: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Call a Home Assistant service (e.g. ``light.turn_on``)."""
        payload: dict[str, Any] = data.copy() if data else {}
        if entity_id:
            payload["entity_id"] = entity_id
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{self.url}/api/services/{domain}/{service}",
                headers=self._headers(),
                json=payload,
            )
            resp.raise_for_status()
            return resp.json()

    async def get_services(self) -> list[dict[str, Any]]:
        """List all available services."""
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                f"{self.url}/api/services", headers=self._headers()
            )
            resp.raise_for_status()
            return resp.json()
