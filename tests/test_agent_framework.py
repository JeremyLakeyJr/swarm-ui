"""Tests for the Microsoft Agent Framework integration."""

from __future__ import annotations

import pytest

from backend.integrations.agent_framework_client import (
    AgentFrameworkTask,
    AgentFrameworkResult,
    AgentFrameworkClient,
)


class TestAgentFrameworkDataClasses:
    """Basic data-class tests."""

    def test_task_defaults(self):
        task = AgentFrameworkTask(prompt="hello")
        assert task.prompt == "hello"
        assert task.agent_name == "swarm_agent"
        assert task.instructions == ""
        assert task.model == ""
        assert task.metadata == {}

    def test_task_custom_values(self):
        task = AgentFrameworkTask(
            prompt="summarize",
            agent_name="custom_agent",
            instructions="Be brief.",
            model="gpt-4",
            metadata={"source": "test"},
        )
        assert task.agent_name == "custom_agent"
        assert task.instructions == "Be brief."
        assert task.model == "gpt-4"
        assert task.metadata == {"source": "test"}

    def test_result_success(self):
        result = AgentFrameworkResult(success=True, summary="done")
        assert result.success is True
        assert result.summary == "done"
        assert result.error is None

    def test_result_failure(self):
        result = AgentFrameworkResult(success=False, error="oops")
        assert result.success is False
        assert result.error == "oops"


class TestAgentFrameworkClient:
    """Tests for AgentFrameworkClient (graceful import failure)."""

    @pytest.mark.asyncio
    async def test_run_task_missing_import(self, monkeypatch):
        """When agent-framework is not installed, run_task should return a
        friendly error."""
        import backend.integrations.agent_framework_client as mod

        async def _fake(self, task):
            return AgentFrameworkResult(
                success=False,
                error="agent-framework is not installed. Run: pip install agent-framework-core --pre",
            )

        monkeypatch.setattr(mod.AgentFrameworkClient, "run_task", _fake)
        client = AgentFrameworkClient()
        result = await client.run_task(AgentFrameworkTask(prompt="test"))
        assert result.success is False
        assert "not installed" in (result.error or "")

    @pytest.mark.asyncio
    async def test_health_check_available(self):
        """Health check should return True when the package is importable."""
        client = AgentFrameworkClient()
        result = await client.health_check()
        # agent-framework-core is installed in the test environment
        assert result is True

    @pytest.mark.asyncio
    async def test_health_check_unavailable(self, monkeypatch):
        """Health check should return False when the package is missing."""
        import builtins

        original_import = builtins.__import__

        def _mock_import(name, *args, **kwargs):
            if name == "agent_framework":
                raise ImportError("mocked")
            return original_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", _mock_import)
        client = AgentFrameworkClient()
        result = await client.health_check()
        assert result is False
