"""Autogen agent orchestration integration.

Wraps Microsoft Autogen's stable API to provide multi-agent workflows
driven by the Ollama LLM backend.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentTask:
    """Describes a task to be executed by an Autogen agent team."""

    prompt: str
    max_rounds: int = 10
    timeout: int = 120
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResult:
    """Holds the outcome of an agent orchestration run."""

    success: bool
    messages: list[dict[str, Any]] = field(default_factory=list)
    summary: str = ""
    error: str | None = None


class AutogenOrchestrator:
    """Manage multi-agent conversations using Autogen's agent-chat API.

    The orchestrator creates a simple two-agent team (an assistant backed
    by the configured LLM and a user-proxy) and runs the conversation for
    the requested number of rounds.
    """

    def __init__(
        self,
        llm_provider: str = "ollama",
        model: str = "llama3",
        base_url: str = "http://localhost:11434",
        max_rounds: int = 10,
        timeout: int = 120,
    ):
        self.llm_provider = llm_provider
        self.model = model
        self.base_url = base_url
        self.max_rounds = max_rounds
        self.timeout = timeout

    async def run_task(self, task: AgentTask) -> AgentResult:
        """Execute *task* through the Autogen agent framework.

        The implementation dynamically imports ``autogen_agentchat`` so the
        rest of the application can start even when the library is missing.
        """
        try:
            from autogen_agentchat.agents import AssistantAgent
            from autogen_agentchat.teams import RoundRobinGroupChat
            from autogen_agentchat.conditions import MaxMessageTermination
            from autogen_ext.models.openai import OpenAIChatCompletionClient
        except ImportError:
            return AgentResult(
                success=False,
                error=(
                    "autogen-agentchat is not installed. "
                    "Run: pip install autogen-agentchat autogen-ext[openai]"
                ),
            )

        try:
            model_client = OpenAIChatCompletionClient(
                model=self.model,
                base_url=f"{self.base_url}/v1",
                api_key="unused",
            )

            assistant = AssistantAgent(
                name="swarm_assistant",
                model_client=model_client,
                system_message=(
                    "You are a helpful AI assistant integrated into Swarm UI. "
                    "Answer questions clearly and concisely."
                ),
            )

            termination = MaxMessageTermination(
                max_messages=task.max_rounds or self.max_rounds,
            )
            team = RoundRobinGroupChat(
                participants=[assistant],
                termination_condition=termination,
            )

            result = await team.run(task=task.prompt)
            messages = [
                {"role": msg.source, "content": getattr(msg, "content", str(msg))}
                for msg in result.messages
            ]
            summary = messages[-1]["content"] if messages else ""
            return AgentResult(success=True, messages=messages, summary=summary)

        except Exception as exc:  # noqa: BLE001
            return AgentResult(success=False, error=str(exc))
