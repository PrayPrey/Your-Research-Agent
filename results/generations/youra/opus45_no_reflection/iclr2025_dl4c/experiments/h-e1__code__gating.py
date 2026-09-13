"""Execution gating for EVAF H-E1."""

import re
import os
import subprocess
import tempfile
from config import CONFIG


def extract_code_from_response(response: str) -> str | None:
    """Extract first ```python ... ``` fenced block from response."""
    pattern = r"```python\s*\n(.*?)```"
    match = re.search(pattern, response, re.DOTALL)
    if match:
        return match.group(1).strip()
    pattern_alt = r"```\s*\n(.*?)```"
    match_alt = re.search(pattern_alt, response, re.DOTALL)
    if match_alt:
        code = match_alt.group(1).strip()
        if "def " in code:
            return code
    return None


def classify_error(stderr: str) -> str:
    """Classify error type from stderr."""
    stderr_lower = stderr.lower()
    if "syntaxerror" in stderr_lower:
        return "syntax_error"
    if "timeout" in stderr_lower or "timed out" in stderr_lower:
        return "timeout"
    if "assertionerror" in stderr_lower:
        return "test_failure"
    if "nameerror" in stderr_lower or "typeerror" in stderr_lower or "attributeerror" in stderr_lower:
        return "runtime_error"
    if "error" in stderr_lower:
        return "runtime_error"
    return "test_failure"


def run_unit_tests(code: str, test_code: str, entry_point: str, timeout: float = None) -> dict:
    """Run code + test_code in subprocess with timeout."""
    timeout = timeout if timeout is not None else CONFIG["test_timeout_s"]

    script = f"""{code}

{test_code}

check({entry_point})
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(script)
        tmp_path = f.name

    try:
        restricted_env = {k: v for k, v in os.environ.items()
                         if not k.startswith(('http', 'HTTP', 'ftp', 'FTP'))}
        restricted_env['PYTHONDONTWRITEBYTECODE'] = '1'

        proc = subprocess.run(
            ["python", tmp_path],
            timeout=timeout,
            capture_output=True,
            text=True,
            env=restricted_env,
            cwd=tempfile.gettempdir(),
        )

        if proc.returncode == 0:
            return {"all_passed": True, "error": None}
        else:
            error_msg = proc.stderr[-2000:] if proc.stderr else "Unknown error"
            return {"all_passed": False, "error": error_msg}

    except subprocess.TimeoutExpired:
        return {"all_passed": False, "error": "timeout"}
    except Exception as e:
        return {"all_passed": False, "error": str(e)}
    finally:
        try:
            os.unlink(tmp_path)
        except:
            pass


def evaf_gate(problem: dict, failing_code: str, feedback_model) -> dict:
    """Full EVAF step: critique -> extract -> test -> decide."""
    response = feedback_model.critique(problem, failing_code)
    code = extract_code_from_response(response)

    if code is None:
        return {
            "accepted": False,
            "suggestion": response,
            "has_code_suggestion": False,
            "rejection_reason": "no_code_block",
        }

    result = run_unit_tests(code, problem["test"], problem["entry_point"])

    if result["all_passed"]:
        return {
            "accepted": True,
            "suggestion": code,
            "has_code_suggestion": True,
            "rejection_reason": None,
        }

    return {
        "accepted": False,
        "suggestion": code,
        "has_code_suggestion": True,
        "rejection_reason": classify_error(result["error"]),
    }
