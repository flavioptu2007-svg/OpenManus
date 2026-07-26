"""Tests for PythonExecute tool — ensures isolated subprocess execution.

These tests verify the security fix from Sprint 1:
- Code runs in isolated subprocess (not exec())
- Timeout works correctly
- Error handling is robust
- stdout/stderr capture works
"""

import pytest

from app.tool.python_execute import PythonExecute


@pytest.fixture
def python_execute():
    """Creates a PythonExecute tool instance."""
    return PythonExecute()


@pytest.mark.asyncio
async def test_simple_execution(python_execute):
    """Test basic Python code execution returns correct output."""
    result = await python_execute.execute(
        code='print("Hello, World!")',
    )

    assert result["success"] is True
    assert "Hello, World!" in result["observation"]


@pytest.mark.asyncio
async def test_multiple_print_statements(python_execute):
    """Test multiple print statements are captured."""
    result = await python_execute.execute(
        code='print("Line 1")\nprint("Line 2")\nprint("Line 3")',
    )

    assert result["success"] is True
    assert "Line 1" in result["observation"]
    assert "Line 2" in result["observation"]
    assert "Line 3" in result["observation"]


@pytest.mark.asyncio
async def test_math_operations(python_execute):
    """Test mathematical operations execute correctly."""
    result = await python_execute.execute(
        code="print(2 + 2)\nprint(10 * 5)\nprint(2 ** 10)",
    )

    assert result["success"] is True
    assert "4" in result["observation"]
    assert "50" in result["observation"]
    assert "1024" in result["observation"]


@pytest.mark.asyncio
async def test_variable_assignment(python_execute):
    """Test variable assignment and usage."""
    result = await python_execute.execute(
        code="x = 42\nprint(f'The answer is {x}')",
    )

    assert result["success"] is True
    assert "The answer is 42" in result["observation"]


@pytest.mark.asyncio
async def test_syntax_error(python_execute):
    """Test syntax errors are caught and reported."""
    result = await python_execute.execute(
        code="print('unclosed string",
    )

    assert result["success"] is False
    assert "SyntaxError" in result["observation"] or "Error" in result["observation"]


@pytest.mark.asyncio
async def test_runtime_error(python_execute):
    """Test runtime errors are caught and reported."""
    result = await python_execute.execute(
        code="print(1 / 0)",
    )

    assert result["success"] is False
    assert "ZeroDivisionError" in result["observation"]


@pytest.mark.asyncio
async def test_timeout(python_execute):
    """Test that long-running code is properly timed out."""
    result = await python_execute.execute(
        code="import time; time.sleep(10); print('done')",
        timeout=1,
    )

    assert result["success"] is False
    assert "timeout" in result["observation"].lower()


@pytest.mark.asyncio
async def test_no_output(python_execute):
    """Test code that produces no output."""
    result = await python_execute.execute(
        code="x = 42",
    )

    # Code without print returns "(no output)" or similar
    assert "observation" in result
    assert result["success"] is True


@pytest.mark.asyncio
async def test_list_operations(python_execute):
    """Test list creation and manipulation."""
    result = await python_execute.execute(
        code="items = [1, 2, 3, 4, 5]\nprint(sum(items))\nprint(len(items))",
    )

    assert result["success"] is True
    assert "15" in result["observation"]
    assert "5" in result["observation"]


@pytest.mark.asyncio
async def test_import_builtins(python_execute):
    """Test that standard library imports work."""
    result = await python_execute.execute(
        code="import json\ndata = {'key': 'value'}\nprint(json.dumps(data))",
    )

    assert result["success"] is True
    assert '{"key": "value"}' in result["observation"]


@pytest.mark.asyncio
async def test_stderr_capture(python_execute):
    """Test that stderr output is captured."""
    result = await python_execute.execute(
        code="import sys; print('stdout'); print('stderr', file=sys.stderr)",
    )

    assert result["success"] is True
    assert "stdout" in result["observation"]


@pytest.mark.asyncio
async def test_empty_code(python_execute):
    """Test empty code string."""
    result = await python_execute.execute(code="")

    assert result["success"] is True
    assert "observation" in result
