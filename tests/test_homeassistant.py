"""Tests for the Home Assistant integration client."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import httpx
import pytest

from backend.integrations.homeassistant import HomeAssistantClient


@pytest.fixture
def client():
    return HomeAssistantClient(
        url="http://ha-test:8123", token="test-token"
    )


class TestHomeAssistantClient:
    @pytest.mark.asyncio
    async def test_health_check_ok(self, client):
        mock_resp = httpx.Response(
            200,
            json={"message": "API running."},
            request=httpx.Request("GET", "http://ha-test:8123/api/"),
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
    async def test_get_states(self, client):
        states = [{"entity_id": "light.kitchen", "state": "on"}]
        mock_resp = httpx.Response(
            200,
            json=states,
            request=httpx.Request("GET", "http://ha-test:8123/api/states"),
        )
        with patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_resp):
            result = await client.get_states()
        assert result[0]["entity_id"] == "light.kitchen"

    @pytest.mark.asyncio
    async def test_call_service(self, client):
        mock_resp = httpx.Response(
            200,
            json=[{"entity_id": "light.kitchen", "state": "on"}],
            request=httpx.Request(
                "POST", "http://ha-test:8123/api/services/light/turn_on"
            ),
        )
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_resp):
            result = await client.call_service("light", "turn_on", "light.kitchen")
        assert len(result) == 1
