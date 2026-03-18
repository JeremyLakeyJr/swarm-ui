"""Chat routes – Ollama-backed conversational AI."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from backend.auth.security import require_auth
from backend.integrations.ollama_client import OllamaClient
from backend.models.schemas import ChatRequest, ChatResponse, ChatMessage

router = APIRouter()


@router.get("/models")
async def list_models(_user: dict = Depends(require_auth)):
    """Return models available on the Ollama server."""
    client = OllamaClient()
    models = await client.list_models()
    return {"models": models}


@router.post("/completions", response_model=ChatResponse)
async def chat_completions(
    req: ChatRequest,
    _user: dict = Depends(require_auth),
):
    """Non-streaming chat completion via Ollama."""
    client = OllamaClient()
    messages = [m.model_dump() for m in req.messages]
    result = await client.chat(messages, model=req.model)
    return ChatResponse(
        message=ChatMessage(
            role=result.get("message", {}).get("role", "assistant"),
            content=result.get("message", {}).get("content", ""),
        ),
        model=result.get("model", client.model),
    )


@router.post("/stream")
async def chat_stream(
    req: ChatRequest,
    _user: dict = Depends(require_auth),
):
    """Streaming chat completion (Server-Sent Events)."""
    client = OllamaClient()
    messages = [m.model_dump() for m in req.messages]

    async def _generate():
        import json

        async for chunk in client.chat_stream(messages, model=req.model):
            yield f"data: {json.dumps(chunk)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(_generate(), media_type="text/event-stream")
