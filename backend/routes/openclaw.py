"""OpenClaw routes – pipeline management and data exchange."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from backend.auth.security import require_auth
from backend.integrations.openclaw import OpenClawClient
from backend.models.schemas import PipelineRunRequest, DataSendRequest

router = APIRouter()


@router.get("/pipelines")
async def list_pipelines(_user: dict = Depends(require_auth)):
    """List available OpenClaw pipelines."""
    client = OpenClawClient()
    return await client.list_pipelines()


@router.post("/pipelines/run")
async def run_pipeline(
    req: PipelineRunRequest,
    _user: dict = Depends(require_auth),
):
    """Trigger execution of an OpenClaw pipeline."""
    client = OpenClawClient()
    return await client.run_pipeline(
        pipeline_id=req.pipeline_id,
        params=req.params,
    )


@router.get("/pipelines/runs/{run_id}")
async def get_pipeline_status(
    run_id: str,
    _user: dict = Depends(require_auth),
):
    """Check status of a pipeline run."""
    client = OpenClawClient()
    return await client.get_pipeline_status(run_id)


@router.post("/data")
async def send_data(
    req: DataSendRequest,
    _user: dict = Depends(require_auth),
):
    """Send data to an OpenClaw module endpoint."""
    client = OpenClawClient()
    return await client.send_data(endpoint=req.endpoint, data=req.data)
