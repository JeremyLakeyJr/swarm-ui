"""Tests for the OpenClaw integration client."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import httpx
import pytest

from backend.integrations.openclaw import OpenClawClient


@pytest.fixture
def client():
    return OpenClawClient(base_url="http://oc-test:9000", api_key="key123")


class TestOpenClawClient:
    @pytest.mark.asyncio
    async def test_health_check_ok(self, client):
        mock_resp = httpx.Response(
            200,
            json={"status": "ok"},
            request=httpx.Request("GET", "http://oc-test:9000/health"),
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

    @pytest.mark.asyncio
    async def test_list_pipelines(self, client):
        pipelines = [{"id": "p1", "name": "Pipeline One"}]
        mock_resp = httpx.Response(
            200,
            json=pipelines,
            request=httpx.Request("GET", "http://oc-test:9000/api/pipelines"),
        )
        with patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_resp):
            result = await client.list_pipelines()
        assert result[0]["id"] == "p1"

    @pytest.mark.asyncio
    async def test_run_pipeline(self, client):
        mock_resp = httpx.Response(
            200,
            json={"run_id": "r1", "status": "started"},
            request=httpx.Request("POST", "http://oc-test:9000/api/pipelines/run"),
        )
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_resp):
            result = await client.run_pipeline("p1")
        assert result["run_id"] == "r1"

    @pytest.mark.asyncio
    async def test_send_data(self, client):
        mock_resp = httpx.Response(
            200,
            json={"received": True},
            request=httpx.Request("POST", "http://oc-test:9000/api/ingest"),
        )
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_resp):
            result = await client.send_data("ingest", {"key": "val"})
        assert result["received"] is True
