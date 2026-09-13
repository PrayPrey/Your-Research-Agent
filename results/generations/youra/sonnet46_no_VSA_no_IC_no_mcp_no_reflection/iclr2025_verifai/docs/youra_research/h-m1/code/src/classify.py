import json
import subprocess
import tempfile
import os
import re


RUNTIME_EXCEPTIONS = [
    "TypeError", "AttributeError", "NameError",
    "IndexError", "KeyError", "ValueError", "ImportError",
    "RecursionError", "ZeroDivisionError", "StopIteration",
    "TimeoutExpired",
]

SYNTAX_EXCEPTIONS = ["SyntaxError", "IndentationError", "TabError"]


def classify_bug_type(code: str, execution_result: dict) -> str:
    """
    Classify a failing solution into type_error / runtime_error / logic_error.
    Priority: Pyright static type errors > runtime exception > logic (assertion) error.
    """
    if execution_result.get("passed"):
        return "passed"

    error = execution_result.get("error", "") or ""
    error_type = execution_result.get("error_type", "") or ""

    # Syntax errors → treat as type_error (static detectable)
    if error_type in SYNTAX_EXCEPTIONS or any(e in error for e in SYNTAX_EXCEPTIONS):
        return "type_error"

    # Run Pyright on a temp file
    pyright_errors = _run_pyright(code)
    if pyright_errors:
        return "type_error"

    # Runtime exception (non-assertion)
    if error_type in RUNTIME_EXCEPTIONS or any(e in error for e in RUNTIME_EXCEPTIONS):
        return "runtime_error"

    # Residual: assertion failure / wrong output
    return "logic_error"


def _run_pyright(code: str) -> list:
    """Return list of Pyright error diagnostics for the code string."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp:
        tmp.write(code)
        tmp_path = tmp.name
    try:
        result = subprocess.run(
            ["pyright", "--outputjson", tmp_path],
            capture_output=True, text=True, timeout=15
        )
        try:
            data = json.loads(result.stdout)
            return [d for d in data.get("generalDiagnostics", []) if d.get("severity") == "error"]
        except (json.JSONDecodeError, KeyError):
            return []
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass
