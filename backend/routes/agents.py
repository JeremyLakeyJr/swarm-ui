"""Agent orchestration routes – Autogen-backed multi-agent workflows."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from backend.auth.security import require_auth
from backend.config import get_settings
from backend.integrations.autogen_agent import AutogenOrchestrator, AgentTask
from backend.models.schemas import AgentTaskRequest, AgentTaskResponse

router = APIRouter()


@router.post("/run", response_model=AgentTaskResponse)
async def run_agent_task(
    req: AgentTaskRequest,
    _user: dict = Depends(require_auth),
):
    """Execute a prompt through the Autogen agent team."""
    settings = get_settings()
    orchestrator = AutogenOrchestrator(
        llm_provider=settings.autogen_default_llm_provider,
        model=settings.ollama_model,
        base_url=settings.ollama_base_url,
        max_rounds=settings.autogen_max_rounds,
        timeout=settings.autogen_timeout,
    )
    task = AgentTask(
        prompt=req.prompt,
        max_rounds=req.max_rounds,
        timeout=req.timeout,
        metadata=req.metadata,
    )
    result = await orchestrator.run_task(task)
    return AgentTaskResponse(
        success=result.success,
        messages=result.messages,
        summary=result.summary,
        error=result.error,
    )
