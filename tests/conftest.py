"""Shared fixtures and mocks for OpenManus tests."""

from typing import AsyncGenerator, List, Optional
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio

from app.llm import LLM
from app.schema import AgentState, Memory, Message, ToolCall, Function
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
