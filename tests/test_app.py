"""Tests for the FastAPI application and route registration."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.app import create_app


@pytest.fixture
def app_client():
    app = create_app()
    return TestClient(app)


class TestAppRoutes:
    def test_health_endpoint(self, app_client):
        """The /api/health endpoint should always return 200."""
        resp = app_client.get("/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert "status" in data
        assert "services" in data

    def test_openapi_schema(self, app_client):
        """OpenAPI schema should be accessible."""
        resp = app_client.get("/openapi.json")
        assert resp.status_code == 200
        schema = resp.json()
        assert schema["info"]["title"] == "Swarm UI"

    def test_chat_models_endpoint(self, app_client):
        """Chat models endpoint should be registered and return models when mocked."""
        from unittest.mock import AsyncMock, patch

        mock_models = [{"name": "testmodel"}]
        with patch(
            "backend.integrations.ollama_client.OllamaClient.list_models",
            new_callable=AsyncMock,
            return_value=mock_models,
        ):
            resp = app_client.get("/api/chat/models")
        assert resp.status_code == 200
        assert resp.json()["models"] == mock_models

    def test_index_html(self, app_client):
        """Root path should serve the frontend."""
        resp = app_client.get("/")
        assert resp.status_code == 200
        assert "Swarm UI" in resp.text
