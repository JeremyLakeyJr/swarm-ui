"""Health check route."""

from __future__ import annotations

from fastapi import APIRouter

from backend.integrations.ollama_client import OllamaClient
from backend.integrations.homeassistant import HomeAssistantClient
from backend.integrations.openclaw import OpenClawClient
from backend.integrations.agent_framework_client import AgentFrameworkClient

router = APIRouter()


@router.get("/health")
async def health():
    """Return service-level health status."""
    ollama_ok = await OllamaClient().health_check()
    ha_ok = await HomeAssistantClient().health_check()
    oc_ok = await OpenClawClient().health_check()
    af_ok = await AgentFrameworkClient().health_check()
    return {
        "status": "ok",
        "services": {
            "ollama": "connected" if ollama_ok else "unavailable",
            "homeassistant": "connected" if ha_ok else "unavailable",
            "openclaw": "connected" if oc_ok else "unavailable",
            "agent_framework": "available" if af_ok else "unavailable",
        },
    }
