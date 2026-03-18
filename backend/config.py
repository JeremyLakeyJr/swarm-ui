"""Application configuration loaded from environment variables."""

from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Central configuration – populated from environment / .env file."""

    # Application
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_secret_key: str = "change-me-to-a-random-secret"
    app_debug: bool = False

    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"

    # Autogen
    autogen_default_llm_provider: str = "ollama"
    autogen_max_rounds: int = 10
    autogen_timeout: int = 120

    # Home Assistant
    homeassistant_url: str = "http://homeassistant.local:8123"
    homeassistant_token: str = ""

    # OpenClaw
    openclaw_base_url: str = "http://localhost:9000"
    openclaw_api_key: str = ""

    # Microsoft Agent Framework
    agent_framework_base_url: str = "http://localhost:11434"
    agent_framework_model: str = "llama3"
    agent_framework_api_key: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


def get_settings() -> Settings:
    """Return a cached settings instance."""
    return Settings()
