# Architecture

## Overview

Swarm UI follows a **backend-for-frontend** pattern: a FastAPI server exposes a unified REST API that the single-page frontend consumes. Each external system (Ollama, Autogen, Home Assistant, OpenClaw) is wrapped in a dedicated integration client.

```
┌────────────────────────────────────────────────────┐
│                   Browser (Frontend)               │
│  index.html  ←→  app.js  ←→  REST API calls       │
└────────────────────┬───────────────────────────────┘
                     │ HTTP / SSE
┌────────────────────▼───────────────────────────────┐
│              FastAPI Backend (backend/app.py)       │
│                                                    │
│  ┌─────────┐ ┌──────────┐ ┌─────────┐ ┌────────┐  │
│  │  Chat   │ │  Agents  │ │   HA    │ │OpenClaw│  │
│  │ Routes  │ │  Routes  │ │ Routes  │ │ Routes │  │
│  └────┬────┘ └────┬─────┘ └────┬────┘ └───┬────┘  │
│       │           │            │           │       │
│  ┌────▼────┐ ┌────▼─────┐ ┌───▼────┐ ┌────▼───┐   │
│  │ Ollama  │ │ Autogen  │ │  HA    │ │OpenClaw│   │
│  │ Client  │ │Orchestr. │ │ Client │ │ Client │   │
│  └────┬────┘ └────┬─────┘ └───┬────┘ └────┬───┘   │
└───────┼───────────┼────────────┼───────────┼───────┘
        │           │            │           │
   ┌────▼────┐ ┌────▼─────┐ ┌───▼────┐ ┌────▼───┐
   │ Ollama  │ │ Ollama   │ │  Home  │ │OpenClaw│
   │ Server  │ │ (via AG) │ │ Assist │ │ Server │
   └─────────┘ └──────────┘ └────────┘ └────────┘
```

In addition, the **Microsoft Agent Framework** integration provides a
separate agent execution path:

```
┌──────────────────────────────────────────┐
│  FastAPI Backend                         │
│  ┌─────────────────────┐                 │
│  │ Agent Framework     │                 │
│  │ Routes              │                 │
│  └─────────┬───────────┘                 │
│  ┌─────────▼───────────┐                 │
│  │ AgentFrameworkClient │                │
│  │ (agent-framework SDK)│                │
│  └─────────┬───────────┘                 │
└────────────┼─────────────────────────────┘
             │
        ┌────▼─────┐
        │  LLM     │
        │ Provider │
        │(Ollama / │
        │ OpenAI)  │
        └──────────┘
```

## Key Design Decisions

1. **Async everywhere** – All integration clients use `httpx.AsyncClient` for non-blocking I/O.
2. **Lazy imports** – Autogen and python-jose are imported on demand so the application can start even when optional dependencies are missing.
3. **Configuration via environment** – All secrets and URLs live in `.env`; `pydantic-settings` validates them at startup.
4. **JWT authentication** – In development mode (default secret key) auth is bypassed; in production a valid Bearer token is required.
5. **Streaming** – Chat supports Server-Sent Events for real-time token delivery.

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Backend framework | FastAPI + Uvicorn |
| AI inference | Ollama |
| Agent orchestration | Microsoft Autogen |
| Agent framework | Microsoft Agent Framework |
| Smart home | Home Assistant REST API |
| Data pipelines | OpenClaw |
| Frontend | Vanilla HTML/CSS/JS |
| Auth | JWT (python-jose) |
| Config | pydantic-settings + python-dotenv |
| Container | Docker + Docker Compose |
