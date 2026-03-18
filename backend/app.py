"""Swarm UI – FastAPI application entry point."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from backend.config import get_settings
from backend.routes.chat import router as chat_router
from backend.routes.agents import router as agents_router
from backend.routes.homeassistant import router as ha_router
from backend.routes.openclaw import router as openclaw_router
from backend.routes.agent_framework import router as af_router
from backend.routes.health import router as health_router


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="Swarm UI",
        description=(
            "AI-powered interface integrating Ollama, Autogen, "
            "Home Assistant, OpenClaw, and Microsoft Agent Framework."
        ),
        version="0.1.0",
        debug=settings.app_debug,
    )

    # CORS – restrict in production via environment
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # API routes
    app.include_router(health_router, prefix="/api", tags=["health"])
    app.include_router(chat_router, prefix="/api/chat", tags=["chat"])
    app.include_router(agents_router, prefix="/api/agents", tags=["agents"])
    app.include_router(ha_router, prefix="/api/homeassistant", tags=["homeassistant"])
    app.include_router(openclaw_router, prefix="/api/openclaw", tags=["openclaw"])
    app.include_router(af_router, prefix="/api/agent-framework", tags=["agent-framework"])

    # Serve frontend static files
    frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
    if os.path.isdir(frontend_dir):
        app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

        @app.get("/")
        async def serve_index():
            return FileResponse(os.path.join(frontend_dir, "index.html"))

    return app


app = create_app()
