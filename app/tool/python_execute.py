import asyncio
from typing import Dict

from app.tool.base import BaseTool


class PythonExecute(BaseTool):
    """A tool for executing Python code with timeout in an isolated subprocess.

    Security: Code is executed in a separate Python process (not via exec()),
    providing process-level isolation. The calling process cannot be accessed.
    """

    name: str = "python_execute"
    description: str = (
        "Executes Python code string in an isolated subprocess. Note: Only print outputs are visible, function return values are not captured. Use print statements to see results."
    )
    parameters: dict = {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "The Python code to execute.",
            },
        },
        "required": ["code"],
    }

    async def execute(  # type: ignore[override]
        self,
        code: str,
        timeout: int = 30,
    ) -> Dict:
        """
        Executes the provided Python code in an isolated subprocess.

        Uses `python3 -c` via asyncio subprocess, which provides complete
        process-level isolation. The code cannot access the parent process's
        memory, imports, or file handles beyond standard permissions.

        Args:
            code (str): The Python code to execute.
            timeout (int): Execution timeout in seconds (default: 30).

        Returns:
            Dict: Contains 'observation' with output and 'success' boolean.
        """
        try:
            # Use subprocess to run code in isolated Python process
            # The -u flag ensures unbuffered output (no output loss on timeout)
            # -c flag passes the code as a string
            proc = await asyncio.create_subprocess_exec(
                "python3",
                "-u",
                "-c",
                code,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(), timeout=timeout
                )
            except asyncio.TimeoutError:
                # Kill the subprocess on timeout
                try:
                    proc.kill()
                    await proc.wait()
                except ProcessLookupError:
                    pass
                return {
                    "observation": f"Execution timeout after {timeout} seconds",
                    "success": False,
                }

            output = stdout.decode("utf-8", errors="replace")
            error_output = stderr.decode("utf-8", errors="replace")

            if error_output:
                output += f"\n[Stderr]: {error_output}"

            return {
                "observation": output if output else "(no output)",
                "success": proc.returncode == 0,
            }

        except FileNotFoundError:
            return {
                "observation": "Error: 'python3' not found. Is Python 3 installed and in PATH?",
                "success": False,
            }
        except Exception as e:
            return {
                "observation": f"Execution error: {str(e)}",
                "success": False,
            }
