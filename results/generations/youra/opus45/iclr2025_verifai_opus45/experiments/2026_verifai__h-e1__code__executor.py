"""Subprocess code execution and error categorization for H-E1."""

import subprocess
from enum import Enum
from typing import Optional


class ErrorCategory(Enum):
    """Categories of code execution outcomes."""
    PASS = "pass"
    RUNTIME_ERROR = "runtime_error"
    WRONG_OUTPUT = "wrong_output"
    SYNTAX_ERROR = "syntax_error"
    TIMEOUT = "timeout"


def execute_code(
    code: str,
    tests: list[str],
    timeout: int = 10,
) -> tuple[ErrorCategory, Optional[str]]:
    """Run code with tests in subprocess.

    Args:
        code: Generated Python code
        tests: List of test assertion strings
        timeout: Execution timeout in seconds

    Returns:
        Tuple of (ErrorCategory, stderr string or None)
    """
    full_code = code + "\n" + "\n".join(tests)
    try:
        result = subprocess.run(
            ["python", "-c", full_code],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        category = categorize_stderr(result.returncode, result.stderr)
        stderr = result.stderr if category != ErrorCategory.PASS else None
        return category, stderr
    except subprocess.TimeoutExpired:
        return ErrorCategory.TIMEOUT, None


def categorize_stderr(returncode: int, stderr: str) -> ErrorCategory:
    """Map returncode and stderr content to ErrorCategory.

    Priority order:
    1. returncode == 0 -> PASS
    2. "SyntaxError" in stderr -> SYNTAX_ERROR
    3. "Traceback (most recent call last):" in stderr -> RUNTIME_ERROR
    4. else -> WRONG_OUTPUT (assertion failures without traceback)

    Args:
        returncode: Process return code
        stderr: Standard error output

    Returns:
        ErrorCategory enum value
    """
    if returncode == 0:
        return ErrorCategory.PASS
    if "SyntaxError" in stderr:
        return ErrorCategory.SYNTAX_ERROR
    if "Traceback (most recent call last):" in stderr:
        return ErrorCategory.RUNTIME_ERROR
    return ErrorCategory.WRONG_OUTPUT
