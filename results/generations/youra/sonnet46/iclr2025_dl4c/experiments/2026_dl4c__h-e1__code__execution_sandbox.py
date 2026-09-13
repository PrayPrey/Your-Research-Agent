"""Subprocess-based code execution sandbox with timeout."""
import os
import subprocess
import tempfile
import logging

logger = logging.getLogger(__name__)


def execute_code(
    code: str,
    stdin: str,
    timeout: float = 5.0,
) -> tuple[str, bool]:
    """Write code to tempfile, run with subprocess, inject stdin.

    Returns:
        (stdout, success) where success=True means returncode==0.
    """
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
            f.write(code)
            tmp_path = f.name

        result = subprocess.run(
            ["python3", tmp_path],
            input=stdin,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        stdout = result.stdout
        success = result.returncode == 0
        return stdout, success

    except subprocess.TimeoutExpired:
        return "", False
    except OSError:
        return "", False
    except Exception as e:
        logger.debug(f"execute_code unexpected error: {e}")
        return "", False
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


def run_against_test_cases(
    code: str,
    test_cases: list[dict],
    timeout: float = 5.0,
) -> int:
    """Run code against all test cases.

    Args:
        code: Python source code string.
        test_cases: list of dicts with 'input' and 'output' keys.
        timeout: seconds per test case execution.

    Returns:
        tests_passed count in [0, T].
    """
    tests_passed = 0
    for tc in test_cases:
        stdin_str = tc.get("input", "")
        expected = tc.get("output", "").strip()
        try:
            stdout, success = execute_code(code, stdin=stdin_str, timeout=timeout)
            if success and stdout.strip() == expected:
                tests_passed += 1
        except Exception:
            pass  # any unhandled error counts as failure; continue
    return tests_passed
