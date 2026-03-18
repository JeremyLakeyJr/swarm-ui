"""Microsoft Agent Framework routes – single-agent task execution."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from backend.auth.security import require_auth
from backend.config import get_settings
from backend.integrations.agent_framework_client import (
    AgentFrameworkClient,
    AgentFrameworkTask,
)
from backend.models.schemas import (
    AgentFrameworkRunRequest,
    AgentFrameworkRunResponse,
)

router = APIRouter()


@router.post("/run", response_model=AgentFrameworkRunResponse)
async def run_agent_framework_task(
    req: AgentFrameworkRunRequest,
    _user: dict = Depends(require_auth),
):
    """Execute a prompt through the Microsoft Agent Framework."""
    settings = get_settings()
    client = AgentFrameworkClient(
        model=settings.agent_framework_model,
        base_url=settings.agent_framework_base_url,
        api_key=settings.agent_framework_api_key,
    )
    task = AgentFrameworkTask(
        prompt=req.prompt,
        agent_name=req.agent_name,
        instructions=req.instructions,
        model=req.model,
        metadata=req.metadata,
    )
    result = await client.run_task(task)
    return AgentFrameworkRunResponse(
        success=result.success,
        messages=result.messages,
        summary=result.summary,
        error=result.error,
    )
