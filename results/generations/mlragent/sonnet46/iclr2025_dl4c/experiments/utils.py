"""
Utility functions for HierAlign experiment.
"""
import ast
import sys
import io
import traceback
import signal
import resource
from typing import Optional


def check_syntax(code: str) -> tuple[bool, str]:
    """Check if code is syntactically valid Python."""
    try:
        ast.parse(code)
        return True, ""
    except SyntaxError as e:
        return False, str(e)


def run_code_with_timeout(code: str, test_input=None, timeout=5) -> dict:
    """
    Execute code and capture result, exception info, and output.
    Returns dict with: success, error_type, error_msg, stdout
    """
    result = {"success": False, "error_type": None, "error_msg": "", "stdout": ""}

    # Check syntax first
    syntax_ok, syntax_err = check_syntax(code)
    if not syntax_ok:
        result["error_type"] = "SyntaxError"
        result["error_msg"] = syntax_err
        return result

    old_stdout = sys.stdout
    sys.stdout = io.StringIO()

    try:
        # Set memory limit
        exec_globals = {}
        exec(code, exec_globals)
        result["success"] = True
        result["stdout"] = sys.stdout.getvalue()
    except Exception as e:
        result["error_type"] = type(e).__name__
        result["error_msg"] = str(e)
        result["stdout"] = sys.stdout.getvalue()
    finally:
        sys.stdout = old_stdout

    return result


def run_test_case(code: str, test_code: str, timeout: int = 5) -> dict:
    """Run a single test case against generated code."""
    result = {"passed": False, "error_type": None, "error_msg": ""}

    full_code = code + "\n" + test_code

    syntax_ok, syntax_err = check_syntax(full_code)
    if not syntax_ok:
        result["error_type"] = "SyntaxError"
        result["error_msg"] = syntax_err
        return result

    old_stdout = sys.stdout
    sys.stdout = io.StringIO()

    try:
        exec_globals = {}
        exec(full_code, exec_globals)
        result["passed"] = True
    except AssertionError as e:
        result["error_type"] = "AssertionError"
        result["error_msg"] = str(e)
    except Exception as e:
        result["error_type"] = type(e).__name__
        result["error_msg"] = str(e)
    finally:
        sys.stdout = old_stdout

    return result


def extract_function_name(code: str) -> Optional[str]:
    """Extract the first function name from code."""
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                return node.name
    except Exception:
        pass
    return None


def extract_code_from_response(response: str) -> str:
    """Extract Python code from LLM response (strip markdown fences)."""
    if "```python" in response:
        start = response.find("```python") + 9
        end = response.find("```", start)
        if end != -1:
            return response[start:end].strip()
    if "```" in response:
        start = response.find("```") + 3
        end = response.find("```", start)
        if end != -1:
            return response[start:end].strip()
    return response.strip()
