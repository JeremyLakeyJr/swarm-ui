"""Home Assistant routes – smart home device control."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from backend.auth.security import require_auth
from backend.integrations.homeassistant import HomeAssistantClient
from backend.models.schemas import ServiceCallRequest

router = APIRouter()


@router.get("/states")
async def get_states(_user: dict = Depends(require_auth)):
    """Fetch all entity states from Home Assistant."""
    client = HomeAssistantClient()
    return await client.get_states()


@router.get("/states/{entity_id:path}")
async def get_entity_state(
    entity_id: str,
    _user: dict = Depends(require_auth),
):
    """Return the state of a single entity."""
    client = HomeAssistantClient()
    return await client.get_entity_state(entity_id)


@router.post("/services/call")
async def call_service(
    req: ServiceCallRequest,
    _user: dict = Depends(require_auth),
) -> list[dict[str, Any]]:
    """Call a Home Assistant service."""
    client = HomeAssistantClient()
    return await client.call_service(
        domain=req.domain,
        service=req.service,
        entity_id=req.entity_id,
        data=req.data,
    )


@router.get("/services")
async def list_services(_user: dict = Depends(require_auth)):
    """List all available Home Assistant services."""
    client = HomeAssistantClient()
    return await client.get_services()
