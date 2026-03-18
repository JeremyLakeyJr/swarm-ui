"""Tests for configuration management."""

from __future__ import annotations

from backend.config import Settings, get_settings


class TestConfig:
    def test_default_values(self):
        s = Settings()
        assert s.app_port == 8000
        assert s.ollama_model == "llama3"
        assert s.autogen_max_rounds == 10

    def test_get_settings_returns_instance(self):
        s = get_settings()
        assert isinstance(s, Settings)

    def test_custom_values(self):
        s = Settings(
            ollama_base_url="http://custom:1234",
            homeassistant_token="my-token",
        )
        assert s.ollama_base_url == "http://custom:1234"
        assert s.homeassistant_token == "my-token"
