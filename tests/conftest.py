"""Shared fixtures and mocks for OpenManus tests."""

import sys
from unittest.mock import AsyncMock, MagicMock

import pytest


# ---------------------------------------------------------------------------
# Mock heavy / optional dependencies before any app imports so the test suite
# can load even when only a subset of packages is installed.
# ---------------------------------------------------------------------------
def _ensure_mock(name: str) -> None:
    """Insert a MagicMock into sys.modules if the module is not already loaded."""
    if name not in sys.modules:
        sys.modules[name] = MagicMock()


# AWS Bedrock (optional provider)
_ensure_mock("boto3")

# Browser-use (optional, heavy dependency)
for _m in (
    "browser_use",
    "browser_use.browser",
    "browser_use.browser.context",
    "browser_use.browser.browser",
    "browser_use.dom",
    "browser_use.dom.service",
    "browser_use.dom.views",
    "browser_use.dom.events",
    "browser_use.dom.serializer",
    "browser_use.dom.transformer",
):
    _ensure_mock(_m)

# Search engines (optional, not in requirements.txt)
for _m in (
    "baidusearch",
    "baidusearch.baidusearch",
    "duckduckgo_search",
    "googlesearch",
):
    _ensure_mock(_m)

# gymnasium / browsergym (optional)
for _m in (
    "gymnasium",
    "gymnasium.envs",
    "browsergym",
    "browsergym.core",
):
    _ensure_mock(_m)

from app.llm import LLM
from app.schema import Function, Memory, Message, ToolCall
from app.tool.base import BaseTool, ToolResult


class MockTool(BaseTool):
    """A mock tool for testing agent tool execution."""

    name: str = "mock_tool"
    description: str = "A mock tool for testing"
    parameters: dict = {
        "type": "object",
        "properties": {
            "input": {
                "type": "string",
                "description": "Test input",
            },
        },
        "required": ["input"],
    }

    async def execute(self, input: str = "", **kwargs) -> ToolResult:
        return ToolResult(output=f"Executed mock_tool with input: {input}")


class FailingTool(BaseTool):
    """A tool that always fails for testing error handling."""

    name: str = "failing_tool"
    description: str = "A tool that always fails"
    parameters: dict = {
        "type": "object",
        "properties": {},
    }

    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult(error="Intentional failure for testing")


class CleanupTool(BaseTool):
    """A tool with cleanup that tracks if cleanup was called."""

    name: str = "cleanup_tool"
    description: str = "A tool that tracks cleanup"
    parameters: dict = {"type": "object", "properties": {}}
    cleanup_called: bool = False

    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult(output="Cleanup tool executed")

    async def cleanup(self):
        self.cleanup_called = True


@pytest.fixture
def mock_llm():
    """Creates a mock LLM that returns predictable responses.

    Uses spec=LLM so Pydantic isinstance checks pass during agent initialization.
    """
    mock = AsyncMock(spec=LLM)
    mock.ask_tool = AsyncMock()
    mock.ask = AsyncMock()
    mock.ask_with_images = AsyncMock()
    mock.count_tokens = MagicMock(return_value=10)
    mock.count_message_tokens = MagicMock(return_value=50)
    mock.check_token_limit = MagicMock(return_value=True)
    mock.update_token_count = MagicMock()
    mock.model = "gpt-4o"
    mock.max_tokens = 4096
    mock.api_key = "test-key"
    mock.base_url = "https://test.api.com"
    return mock


@pytest.fixture
def mock_tool_call_response():
    """Creates a mock LLM response with real ToolCall/Function objects."""
    response = MagicMock()
    response.tool_calls = [
        ToolCall(
            id="call_1",
            type="function",
            function=Function(name="mock_tool", arguments='{"input": "test_data"}'),
        )
    ]
    response.content = "I will use the mock tool."
    return response


@pytest.fixture
def mock_text_response():
    """Creates a mock LLM response with only text (no tool calls)."""
    response = MagicMock()
    response.tool_calls = None
    response.content = "Here is my text response."
    return response


@pytest.fixture
def agent_memory():
    """Creates an agent memory with some initial messages."""
    memory = Memory()
    memory.add_message(Message.system_message("You are a test assistant."))
    memory.add_message(Message.user_message("Test user message"))
    return memory


@pytest.fixture
def cleanup_tool():
    """Creates a cleanup tool instance."""
    return CleanupTool()
