"""Tests for the Autogen orchestration integration."""

from __future__ import annotations

import pytest

from backend.integrations.autogen_agent import (
    AgentTask,
    AgentResult,
    AutogenOrchestrator,
)


class TestAgentDataClasses:
    """Basic data-class tests."""

    def test_agent_task_defaults(self):
        task = AgentTask(prompt="hello")
        assert task.prompt == "hello"
        assert task.max_rounds == 10
        assert task.timeout == 120
        assert task.metadata == {}

    def test_agent_result_success(self):
        result = AgentResult(success=True, summary="done")
        assert result.success is True
        assert result.summary == "done"
        assert result.error is None

    def test_agent_result_failure(self):
        result = AgentResult(success=False, error="oops")
        assert result.success is False
        assert result.error == "oops"


class TestAutoGenOrchestrator:
    """Tests for AutogenOrchestrator (graceful import failure)."""

    @pytest.mark.asyncio
    async def test_run_task_missing_import(self, monkeypatch):
        """When autogen is not installed, run_task should return a friendly error."""
        import backend.integrations.autogen_agent as mod

        original = mod.AutogenOrchestrator.run_task

        async def _fake(self, task):
            # Simulate ImportError path
            return AgentResult(
                success=False,
                error="autogen-agentchat is not installed. Run: pip install autogen-agentchat autogen-ext[openai]",
            )

        monkeypatch.setattr(mod.AutogenOrchestrator, "run_task", _fake)
        orch = AutogenOrchestrator()
        result = await orch.run_task(AgentTask(prompt="test"))
        assert result.success is False
        assert "not installed" in (result.error or "")
