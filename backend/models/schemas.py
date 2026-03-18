"""Pydantic schemas shared across routes."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


# ------------------------------------------------------------------
# Chat
# ------------------------------------------------------------------


class ChatMessage(BaseModel):
    role: str = Field(..., examples=["user"])
    content: str = Field(..., examples=["Hello, how are you?"])


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    model: str | None = None
    stream: bool = False


class ChatResponse(BaseModel):
    message: ChatMessage
    model: str
    done: bool = True


# ------------------------------------------------------------------
# Agents
# ------------------------------------------------------------------


class AgentTaskRequest(BaseModel):
    prompt: str
    max_rounds: int = 10
    timeout: int = 120
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentTaskResponse(BaseModel):
    success: bool
    messages: list[dict[str, Any]] = Field(default_factory=list)
    summary: str = ""
    error: str | None = None


# ------------------------------------------------------------------
# Home Assistant
# ------------------------------------------------------------------


class ServiceCallRequest(BaseModel):
    domain: str = Field(..., examples=["light"])
    service: str = Field(..., examples=["turn_on"])
    entity_id: str | None = Field(None, examples=["light.living_room"])
    data: dict[str, Any] = Field(default_factory=dict)


# ------------------------------------------------------------------
# OpenClaw
# ------------------------------------------------------------------


class PipelineRunRequest(BaseModel):
    pipeline_id: str
    params: dict[str, Any] = Field(default_factory=dict)


class DataSendRequest(BaseModel):
    endpoint: str
    data: dict[str, Any]


# ------------------------------------------------------------------
# Microsoft Agent Framework
# ------------------------------------------------------------------


class AgentFrameworkRunRequest(BaseModel):
    prompt: str
    agent_name: str = "swarm_agent"
    instructions: str = ""
    model: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentFrameworkRunResponse(BaseModel):
    success: bool
    messages: list[dict[str, Any]] = Field(default_factory=list)
    summary: str = ""
    error: str | None = None


# ------------------------------------------------------------------
# Generic
# ------------------------------------------------------------------


class StatusResponse(BaseModel):
    status: str
    detail: str = ""
