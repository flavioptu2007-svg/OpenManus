"""Tests for ToolCallAgent — the base agent for tool/function calls."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.agent.toolcall import ToolCallAgent
from app.exceptions import TokenLimitExceeded
from app.llm import LLM
from app.schema import AgentState, Function, Message, ToolCall, ToolChoice
from app.tool import Terminate, ToolCollection
from tests.conftest import FailingTool, MockTool


def _make_tool_call(function_name: str, arguments: str = "{}") -> ToolCall:
    """Helper to create a ToolCall with a proper Function model."""
    return ToolCall(
        id="call_1",
        type="function",
        function=Function(name=function_name, arguments=arguments),
    )


@pytest.fixture
def toolcall_agent(mock_llm):
    """Creates a ToolCallAgent instance with mocked LLM."""
    agent = ToolCallAgent(
        name="test_toolcall",
        description="A test toolcall agent",
        llm=mock_llm,
        available_tools=ToolCollection(
            MockTool(),
            FailingTool(),
            Terminate(),
        ),
        special_tool_names=["terminate"],
        max_steps=5,
    )
    return agent


@pytest.mark.asyncio
async def test_agent_initialization(toolcall_agent):
    """Test that agent initializes with correct defaults."""
    assert toolcall_agent.name == "test_toolcall"
    assert toolcall_agent.state == AgentState.IDLE
    assert toolcall_agent.max_steps == 5
    assert toolcall_agent.current_step == 0
    assert len(toolcall_agent.memory.messages) == 0


@pytest.mark.asyncio
async def test_think_with_tool_calls(toolcall_agent, mock_tool_call_response):
    """Test think() when LLM returns tool calls."""
    toolcall_agent.llm.ask_tool = AsyncMock(return_value=mock_tool_call_response)

    result = await toolcall_agent.think()

    assert result is True
    assert len(toolcall_agent.tool_calls) == 1
    assert toolcall_agent.tool_calls[0].function.name == "mock_tool"
    # Should have added the assistant message to memory
    assert len(toolcall_agent.memory.messages) > 0


@pytest.mark.asyncio
async def test_think_with_text_only(toolcall_agent, mock_text_response):
    """Test think() when LLM returns only text (no tool calls)."""
    toolcall_agent.llm.ask_tool = AsyncMock(return_value=mock_text_response)

    result = await toolcall_agent.think()

    assert result is True  # Text content is truthy
    assert len(toolcall_agent.tool_calls) == 0


@pytest.mark.asyncio
async def test_think_with_empty_response(toolcall_agent):
    """Test think() when LLM returns empty response."""
    empty_response = MagicMock()
    empty_response.tool_calls = None
    empty_response.content = ""
    toolcall_agent.llm.ask_tool = AsyncMock(return_value=empty_response)

    result = await toolcall_agent.think()

    assert result is False  # No content and no tool calls
    assert len(toolcall_agent.tool_calls) == 0


@pytest.mark.asyncio
async def test_act_executes_tool_calls(toolcall_agent):
    """Test act() executes tool calls and stores results."""
    tool_call = _make_tool_call("mock_tool", '{"input": "hello"}')
    toolcall_agent.tool_calls = [tool_call]

    result = await toolcall_agent.act()

    assert "Observed output of cmd `mock_tool` executed" in result
    assert "hello" in result
    # Check that tool result was added to memory
    assert len(toolcall_agent.memory.messages) > 0
    last_msg = toolcall_agent.memory.messages[-1]
    assert last_msg.role == "tool"
    assert last_msg.name == "mock_tool"


@pytest.mark.asyncio
async def test_act_with_no_tool_calls(toolcall_agent):
    """Test act() with no tool calls returns last message content."""
    toolcall_agent.tool_calls = []
    toolcall_agent.memory.add_message(Message.assistant_message("Test content"))

    result = await toolcall_agent.act()

    assert result == "Test content"


@pytest.mark.asyncio
async def test_act_with_no_tool_calls_and_no_content(toolcall_agent):
    """Test act() with no tool calls and no content."""
    toolcall_agent.tool_calls = []
    toolcall_agent.memory.add_message(Message.assistant_message(""))

    result = await toolcall_agent.act()

    assert result == "No content or commands to execute"


@pytest.mark.asyncio
async def test_act_required_without_tool_calls_raises(toolcall_agent):
    """Test act() with REQUIRED tool_choice and no tool calls raises ValueError."""
    toolcall_agent.tool_calls = []
    toolcall_agent.tool_choices = ToolChoice.REQUIRED

    with pytest.raises(ValueError, match="Tool calls required but none provided"):
        await toolcall_agent.act()


@pytest.mark.asyncio
async def test_execute_tool_success(toolcall_agent):
    """Test execute_tool with a valid tool call."""
    tool_call = _make_tool_call("mock_tool", '{"input": "world"}')

    result = await toolcall_agent.execute_tool(tool_call)

    assert "Observed output of cmd `mock_tool` executed" in result
    assert "world" in result


@pytest.mark.asyncio
async def test_execute_tool_invalid_name(toolcall_agent):
    """Test execute_tool with unknown tool name returns error."""
    tool_call = _make_tool_call("nonexistent_tool")

    result = await toolcall_agent.execute_tool(tool_call)

    assert "Error: Unknown tool" in result


@pytest.mark.asyncio
async def test_execute_tool_invalid_command(toolcall_agent):
    """Test execute_tool with None command."""
    result = await toolcall_agent.execute_tool(None)
    assert "Error: Invalid command format" in result


@pytest.mark.asyncio
async def test_execute_tool_invalid_json(toolcall_agent):
    """Test execute_tool with invalid JSON arguments."""
    tool_call = _make_tool_call("mock_tool", "not valid json")

    result = await toolcall_agent.execute_tool(tool_call)

    assert "Error parsing arguments" in result
    assert "Invalid JSON" in result


@pytest.mark.asyncio
async def test_execute_tool_failure_result(toolcall_agent):
    """Test execute_tool with a tool that returns failure."""
    tool_call = _make_tool_call("failing_tool")

    result = await toolcall_agent.execute_tool(tool_call)

    assert "Intentional failure" in result


@pytest.mark.asyncio
async def test_special_tool_terminate_changes_state(toolcall_agent):
    """Test that executing 'terminate' special tool sets FINISHED state."""
    tool_call = _make_tool_call("terminate", '{"status": "success"}')

    result = await toolcall_agent.execute_tool(tool_call)

    assert toolcall_agent.state == AgentState.FINISHED
    assert "terminate" in result


@pytest.mark.asyncio
async def test_is_special_tool(toolcall_agent):
    """Test _is_special_tool checks against special_tool_names."""
    assert toolcall_agent._is_special_tool("terminate") is True
    assert toolcall_agent._is_special_tool("mock_tool") is False
    assert toolcall_agent._is_special_tool("unknown") is False


@pytest.mark.asyncio
async def test_step_with_think_and_act(toolcall_agent, mock_tool_call_response):
    """Test the full step() cycle: think → act."""
    toolcall_agent.llm.ask_tool = AsyncMock(return_value=mock_tool_call_response)

    result = await toolcall_agent.step()

    assert "Observed output" in result


@pytest.mark.asyncio
async def test_step_thinking_no_action(toolcall_agent, mock_text_response):
    """Test step() when think says no action needed."""
    toolcall_agent.llm.ask_tool = AsyncMock(return_value=mock_text_response)

    result = await toolcall_agent.step()

    # act() returns the last message content when no tool calls
    assert result == "Here is my text response."


@pytest.mark.asyncio
async def test_run_with_request(toolcall_agent, mock_tool_call_response):
    """Test run() processes a request through the full loop."""
    toolcall_agent.llm.ask_tool = AsyncMock(return_value=mock_tool_call_response)

    # Patch max_steps to 1 for quick test
    toolcall_agent.max_steps = 1

    result = await toolcall_agent.run("Test request")

    assert "Step" in result


@pytest.mark.asyncio
async def test_cleanup_calls_tool_cleanup(cleanup_tool):
    """Test cleanup() invokes cleanup on tools that have it."""
    # Use spec=LLM so the isinstance check in initialize_agent passes
    agent = ToolCallAgent(
        name="test_cleanup",
        description="A test agent",
        llm=MagicMock(spec=LLM),
        available_tools=ToolCollection(cleanup_tool),
        max_steps=1,
    )

    await agent.cleanup()

    assert cleanup_tool.cleanup_called is True


@pytest.mark.asyncio
async def test_run_always_calls_cleanup(toolcall_agent, mock_tool_call_response):
    """Test that run() always calls cleanup, even on error."""
    cleanup_called = False
    original_cleanup = toolcall_agent.cleanup

    async def tracking_cleanup():
        nonlocal cleanup_called
        cleanup_called = True
        await original_cleanup()

    toolcall_agent.cleanup = tracking_cleanup
    toolcall_agent.llm.ask_tool = AsyncMock(return_value=mock_tool_call_response)
    toolcall_agent.max_steps = 1

    await toolcall_agent.run("test")

    assert cleanup_called is True


@pytest.mark.asyncio
async def test_think_with_none_tool_choice(toolcall_agent):
    """Test think() with ToolChoice.NONE."""
    toolcall_agent.tool_choices = ToolChoice.NONE
    text_response = MagicMock()
    text_response.tool_calls = []
    text_response.content = "Response without tools"
    toolcall_agent.llm.ask_tool = AsyncMock(return_value=text_response)

    result = await toolcall_agent.think()

    assert result is True  # Has text content


@pytest.mark.asyncio
async def test_think_with_token_limit_exceeded(toolcall_agent):
    """Test think() handles TokenLimitExceeded gracefully."""
    retry_error = Exception("Retry error")
    retry_error.__cause__ = TokenLimitExceeded("Token limit exceeded")

    async def raise_retry_error(*args, **kwargs):
        raise retry_error

    toolcall_agent.llm.ask_tool = raise_retry_error

    result = await toolcall_agent.think()

    assert result is False  # Should return False (agent finished)
    assert toolcall_agent.state == AgentState.FINISHED


@pytest.mark.asyncio
async def test_think_preserves_next_step_prompt(
    toolcall_agent, mock_tool_call_response
):
    """Test think() restores the original next_step_prompt after processing."""
    original_prompt = "Original prompt"
    toolcall_agent.next_step_prompt = original_prompt
    toolcall_agent.llm.ask_tool = AsyncMock(return_value=mock_tool_call_response)

    await toolcall_agent.think()

    assert toolcall_agent.next_step_prompt == original_prompt
