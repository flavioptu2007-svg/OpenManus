class ToolError(Exception):
    """Raised when a tool encounters an error."""

    def __init__(self, message):
        self.message = message


class OpenManusError(Exception):
    """Base exception for all OpenManus errors"""


class TokenLimitExceededError(OpenManusError):
    """Exception raised when the token limit is exceeded"""


# Backwards-compatible alias: modules still on the pre-rename name
# (app/agent/toolcall.py, tests/test_toolcall_agent.py) keep importing
# TokenLimitExceeded without breaking.
TokenLimitExceeded = TokenLimitExceededError
