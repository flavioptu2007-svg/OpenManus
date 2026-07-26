"""Tests for Bash tool — basic execution and security blocklist.

These tests verify:
- Basic command execution works
- The destructive command blocklist (Sprint 1 security fix)
- Session management
- Error handling
"""

import pytest

from app.exceptions import ToolError
from app.tool.bash import Bash, CLIResult


@pytest.fixture
def bash():
    """Creates a Bash tool instance with fresh session."""
    return Bash()


@pytest.mark.asyncio
async def test_simple_command(bash):
    """Test executing a simple echo command."""
    result = await bash.execute(command="echo 'hello world'")

    assert isinstance(result, CLIResult)
    assert "hello world" in (result.output or "")


@pytest.mark.asyncio
async def test_command_with_output(bash):
    """Test command that produces multiline output."""
    result = await bash.execute(
        command="echo 'line1' && echo 'line2' && echo 'line3'"
    )

    assert isinstance(result, CLIResult)
    assert "line1" in (result.output or "")
    assert "line2" in (result.output or "")
    assert "line3" in (result.output or "")


@pytest.mark.asyncio
async def test_ls_command(bash):
    """Test ls command works."""
    result = await bash.execute(command="ls")

    assert isinstance(result, CLIResult)
    assert result.error is None or result.error == ""


@pytest.mark.asyncio
async def test_pwd_command(bash):
    """Test pwd returns a path."""
    result = await bash.execute(command="pwd")

    assert isinstance(result, CLIResult)
    assert result.output.startswith("/") or result.error == ""


@pytest.mark.asyncio
async def test_restart_session(bash):
    """Test restarting the bash session."""
    # First execute something
    await bash.execute(command="echo 'first'")

    # Restart
    result = await bash.execute(restart=True)

    assert isinstance(result, CLIResult)
    assert result.system == "tool has been restarted."
    # After restart, session should be fresh
    assert bash._session is not None
    assert bash._session._started is True


# --- Blocklist Tests (Sprint 1 Security Fix) ---


@pytest.mark.asyncio
async def test_blocklist_rm_forward_slash(bash):
    """Test that 'rm -rf /' is blocked."""
    with pytest.raises(ToolError, match="blocked for security"):
        await bash.execute(command="rm -rf /var/log")


@pytest.mark.asyncio
async def test_blocklist_rm_root(bash):
    """Test that 'rm -rf ~' is blocked."""
    with pytest.raises(ToolError, match="blocked for security"):
        await bash.execute(command="rm -rf ~/.ssh")


@pytest.mark.asyncio
async def test_blocklist_mkfs(bash):
    """Test that 'mkfs.' commands are blocked."""
    with pytest.raises(ToolError, match="blocked for security"):
        await bash.execute(command="mkfs.ext4 /dev/sdb1")


@pytest.mark.asyncio
async def test_blocklist_dd(bash):
    """Test that 'dd if=' commands are blocked."""
    with pytest.raises(ToolError, match="blocked for security"):
        await bash.execute(command="dd if=/dev/zero of=/dev/sda bs=1M")


@pytest.mark.asyncio
async def test_blocklist_chmod_777(bash):
    """Test that 'chmod 777 /' is blocked."""
    with pytest.raises(ToolError, match="blocked for security"):
        await bash.execute(command="chmod 777 /etc")


@pytest.mark.asyncio
async def test_blocklist_fork_bomb(bash):
    """Test that fork bombs are blocked."""
    with pytest.raises(ToolError, match="blocked for security"):
        await bash.execute(command=":(){ :|:& };")


@pytest.mark.asyncio
async def test_blocklist_reboot(bash):
    """Test that reboot is blocked."""
    with pytest.raises(ToolError, match="blocked for security"):
        await bash.execute(command="reboot")


@pytest.mark.asyncio
async def test_blocklist_shutdown(bash):
    """Test that shutdown is blocked."""
    with pytest.raises(ToolError, match="blocked for security"):
        await bash.execute(command="shutdown now -h")


@pytest.mark.asyncio
async def test_blocklist_halt(bash):
    """Test that halt is blocked."""
    with pytest.raises(ToolError, match="blocked for security"):
        await bash.execute(command="halt -f")


# --- Safe Commands Should Still Work ---

@pytest.mark.asyncio
async def test_safe_command_rm_file(bash):
    """Test that 'rm' without destructive patterns still works."""
    # First create a file, then safely remove it
    await bash.execute(command="touch /tmp/test_manus_safe.txt")
    result = await bash.execute(command="rm /tmp/test_manus_safe.txt")

    assert isinstance(result, CLIResult)


@pytest.mark.asyncio
async def test_safe_command_chmod_normal(bash):
    """Test that chmod with safe paths still works."""
    await bash.execute(command="touch /tmp/test_manus_chmod.txt")
    result = await bash.execute(command="chmod 644 /tmp/test_manus_chmod.txt")

    assert isinstance(result, CLIResult)


@pytest.mark.asyncio
async def test_safe_pipe_commands(bash):
    """Test that piped commands without destructive patterns still work."""
    result = await bash.execute(command="echo 'hello' | grep hello")

    assert isinstance(result, CLIResult)
    assert "hello" in (result.output or "")
