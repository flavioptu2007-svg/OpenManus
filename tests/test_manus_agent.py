"""Tests for Manus agent — the general-purpose agent with MCP support."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.agent.manus import Manus
from app.schema import AgentState, Message, ToolCall


@pytest.fixture
def mock_llm():
    """Creates a properly mocked LLM for Manus tests."""
    from app.llm import LLM
    mock = AsyncMock(spec=LLM)
    mock.ask_tool = AsyncMock()
    mock.ask = AsyncMock()
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
def mock_manus(mock_llm):
    """Creates a Manus instance with mocked dependencies for testing."""
    with (
        patch(
            "app.agent.manus.MCPClients",
            new_callable=MagicMock,
        ) as mock_mcp_cls,
        patch(
            "app.config.config._config.mcp_config",
            new=MagicMock(servers={}),
        ),
    ):
        # Configure MCP client mock
        mock_mcp = MagicMock()
        mock_mcp.tools = []
        mock_mcp.connect_sse = AsyncMock()
        mock_mcp.connect_stdio = AsyncMock()
        mock_mcp.disconnect = AsyncMock()
        mock_mcp_cls.return_value = mock_mcp

        agent = Manus(
            name="test_manus",
            description="Test Manus agent",
            llm=mock_llm,
            max_steps=3,
        )
        agent._initialized = True  # Skip MCP initialization
        return agent


@pytest.mark.asyncio
async def test_manus_initialization(mock_manus):
    """Test that Manus agent initializes with correct defaults."""
    assert mock_manus.name == "test_manus"
    assert mock_manus.state == AgentState.IDLE
    assert mock_manus.max_steps == 3
    assert mock_manus.max_observe == 10000
    assert mock_manus._initialized is True


@pytest.mark.asyncio
async def test_manus_available_tools(mock_manus):
    """Test that Manus has the expected tools available."""
    tool_names = [t.name for t in mock_manus.available_tools.tools]
    assert "python_execute" in tool_names
    assert "browser_use" in tool_names
    assert "str_replace_editor" in tool_names
    assert "terminate" in tool_names
    # ask_human may or may not be included
    assert len(tool_names) >= 4


@pytest.mark.asyncio
async def test_manus_create_factory(mock_llm):
    """Test the create() factory method."""
    with (
        patch("app.agent.manus.MCPClients") as mock_mcp_cls,
        patch("app.config.config._config.mcp_config", new=MagicMock(servers={})),
    ):
        mock_mcp = MagicMock()
        mock_mcp.tools = []
        mock_mcp.connect_sse = AsyncMock()
        mock_mcp.connect_stdio = AsyncMock()
        mock_mcp.disconnect = AsyncMock()
        mock_mcp_cls.return_value = mock_mcp

        agent = await Manus.create(llm=mock_llm, max_steps=2)

        assert agent._initialized is True
        assert agent.name == "Manus"


@pytest.mark.asyncio
async def test_manus_think_with_no_browser(mock_manus, mock_llm):
    """Test think() when browser is not in use."""
    mock_tool_call_response = MagicMock()
    mock_tool_call_response.tool_calls = []
    mock_tool_call_response.content = "No tools needed"
    mock_llm.ask_tool = AsyncMock(return_value=mock_tool_call_response)

    mock_manus.llm = mock_llm
    result = await mock_manus.think()

    assert result is True  # Has text content


@pytest.mark.asyncio
async def test_manus_cleanup(mock_manus):
    """Test cleanup() closes browser and disconnects MCP."""
    mock_manus.browser_context_helper = MagicMock()
    mock_manus.browser_context_helper.cleanup_browser = AsyncMock()
    mock_manus.mcp_clients.disconnect = AsyncMock()
    mock_manus._initialized = True

    await mock_manus.cleanup()

    mock_manus.browser_context_helper.cleanup_browser.assert_called_once()
    mock_manus.mcp_clients.disconnect.assert_called_once()
    assert mock_manus._initialized is False


@pytest.mark.asyncio
async def test_manus_cleanup_without_initialization(mock_manus):
    """Test cleanup() does not disconnect MCP if not initialized."""
    mock_manus.browser_context_helper = MagicMock()
    mock_manus.browser_context_helper.cleanup_browser = AsyncMock()
    mock_manus.mcp_clients.disconnect = AsyncMock()
    mock_manus._initialized = False

    await mock_manus.cleanup()

    mock_manus.browser_context_helper.cleanup_browser.assert_called_once()
    mock_manus.mcp_clients.disconnect.assert_not_called()


@pytest.mark.asyncio
async def test_manus_init_mcp_on_think(mock_manus, mock_llm):
    """Test think() initializes MCP if not already initialized."""
    mock_manus._initialized = False
    mock_manus.initialize_mcp_servers = AsyncMock()

    mock_response = MagicMock()
    mock_response.tool_calls = []
    mock_response.content = "test"
    mock_llm.ask_tool = AsyncMock(return_value=mock_response)
    mock_manus.llm = mock_llm

    await mock_manus.think()

    mock_manus.initialize_mcp_servers.assert_called_once()
    assert mock_manus._initialized is True


@pytest.mark.asyncio
async def test_manus_special_tool_names(mock_manus):
    """Test that terminate is in special tool names."""
    assert "terminate" in mock_manus.special_tool_names


@pytest.mark.asyncio
async def test_manus_browser_context_helper(mock_manus):
    """Test browser_context_helper is properly initialized."""
    assert mock_manus.browser_context_helper is not None
    assert mock_manus.browser_context_helper.agent == mock_manus
