"""OpenClaw integration module.

Provides connectivity to OpenClaw services for data exchange, pipeline
execution, and status monitoring.
"""

from __future__ import annotations

from typing import Any

import httpx

from backend.config import get_settings


class OpenClawClient:
    """Async client for the OpenClaw HTTP API."""

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
    ):
        settings = get_settings()
        self.base_url = (base_url or settings.openclaw_base_url).rstrip("/")
        self.api_key = api_key or settings.openclaw_api_key

    def _headers(self) -> dict[str, str]:
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    async def health_check(self) -> bool:
        """Return True when the OpenClaw server is reachable."""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    f"{self.base_url}/health", headers=self._headers()
                )
                return resp.status_code == 200
        except httpx.HTTPError:
            return False

    async def list_pipelines(self) -> list[dict[str, Any]]:
        """Fetch available OpenClaw pipelines."""
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                f"{self.base_url}/api/pipelines", headers=self._headers()
            )
            resp.raise_for_status()
            return resp.json()

    async def run_pipeline(
        self,
        pipeline_id: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Trigger execution of a pipeline and return its run info."""
        payload: dict[str, Any] = {"pipeline_id": pipeline_id}
        if params:
            payload["params"] = params
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"{self.base_url}/api/pipelines/run",
                headers=self._headers(),
                json=payload,
            )
            resp.raise_for_status()
            return resp.json()

    async def get_pipeline_status(
        self, run_id: str
    ) -> dict[str, Any]:
        """Poll the execution status of a pipeline run."""
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                f"{self.base_url}/api/pipelines/runs/{run_id}",
                headers=self._headers(),
            )
            resp.raise_for_status()
            return resp.json()

    async def send_data(
        self,
        endpoint: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """Send arbitrary data to an OpenClaw module endpoint."""
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{self.base_url}/api/{endpoint.lstrip('/')}",
                headers=self._headers(),
                json=data,
            )
            resp.raise_for_status()
            return resp.json()
