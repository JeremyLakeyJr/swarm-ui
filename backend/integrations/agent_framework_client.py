"""Microsoft Agent Framework integration.

Wraps the ``agent-framework`` SDK to expose a simple async interface for
running AI agents from within Swarm UI.  The integration dynamically imports
the library so the rest of the application can start even when the package
is not installed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from backend.config import get_settings


@dataclass
class AgentFrameworkTask:
    """Describes a task to be executed by an Agent Framework agent."""

    prompt: str
    agent_name: str = "swarm_agent"
    instructions: str = ""
    model: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentFrameworkResult:
    """Holds the outcome of an Agent Framework run."""

    success: bool
    messages: list[dict[str, Any]] = field(default_factory=list)
    summary: str = ""
    error: str | None = None


class AgentFrameworkClient:
    """Run agents using the Microsoft Agent Framework.

    The client connects to the configured LLM provider (defaulting to Ollama's
    OpenAI-compatible endpoint) and creates a single ``Agent`` to execute the
    requested task.
    """

    def __init__(
        self,
        model: str = "",
        base_url: str = "",
        api_key: str = "",
    ):
        settings = get_settings()
        self.model = model or settings.agent_framework_model
        self.base_url = (base_url or settings.agent_framework_base_url).rstrip("/")
        self.api_key = api_key or settings.agent_framework_api_key

    async def run_task(self, task: AgentFrameworkTask) -> AgentFrameworkResult:
        """Execute *task* through the Microsoft Agent Framework.

        The implementation dynamically imports ``agent_framework`` so the rest
        of the application can start even when the library is missing.
        """
        try:
            from agent_framework import Agent, Message
            from agent_framework.openai import OpenAIChatClient
        except ImportError:
            return AgentFrameworkResult(
                success=False,
                error=(
                    "agent-framework is not installed. "
                    "Run: pip install agent-framework-core --pre"
                ),
            )

        try:
            client = OpenAIChatClient(
                model_id=task.model or self.model,
                base_url=f"{self.base_url}/v1",
                api_key=self.api_key or "unused",
            )

            instructions = task.instructions or (
                "You are a helpful AI assistant integrated into Swarm UI. "
                "Answer questions clearly and concisely."
            )

            agent = Agent(
                client=client,
                name=task.agent_name,
                instructions=instructions,
            )

            input_msg = Message(role="user", text=task.prompt)
            response = await agent.run(input_msg)

            messages: list[dict[str, Any]] = []
            if response.messages:
                resp_msgs = (
                    response.messages
                    if isinstance(response.messages, list)
                    else [response.messages]
                )
                for msg in resp_msgs:
                    msg_dict = msg.to_dict()
                    role = msg_dict.get("role", "assistant")
                    text = msg.text or ""
                    messages.append({"role": role, "content": text})

            summary = messages[-1]["content"] if messages else ""
            return AgentFrameworkResult(
                success=True,
                messages=messages,
                summary=summary,
            )

        except Exception as exc:  # noqa: BLE001
            return AgentFrameworkResult(
                success=False,
                error=f"{type(exc).__name__}: {exc}",
            )

    async def health_check(self) -> bool:
        """Return ``True`` when the agent-framework package is importable."""
        try:
            import agent_framework  # noqa: F401

            return True
        except ImportError:
            return False
