"""H-M2: Execution analysis with evalplus test format (HumanEval + MBPP)."""
import subprocess
import tempfile
import sys
from pathlib import Path
from typing import Set


def run_execution_tests(problem_id: str, code: str, problem: dict, timeout: int = 10) -> Set[str]:
    """Run evalplus test suite on code, return failure type set.

    HumanEval+ uses `check(candidate)` pattern.
    MBPP+ uses direct `assertion` statements.
    """
    failures = set()

    entry_point = problem.get("entry_point", "")
    test_code_str = problem.get("test", "")
    assertion_str = problem.get("assertion", "")

    if not entry_point:
        return failures

    # HumanEval+ format: test with check(candidate)
    if test_code_str:
        full_test = f"""
{code}

# Bind the solution function as 'candidate' for evalplus tests
candidate = {entry_point}

{test_code_str}

# Run the check
try:
    check(candidate)
except AssertionError as e:
    import sys
    print(f"ASSERTION_FAILED: {{e}}", file=sys.stderr)
    sys.exit(1)
except TypeError as e:
    import sys
    print(f"TYPE_ERROR: {{e}}", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    import sys
    print(f"RUNTIME_ERROR: {{type(e).__name__}}: {{e}}", file=sys.stderr)
    sys.exit(1)
"""
        result = _run_test_code(full_test, timeout)
        if result:
            failures.add(result)
            return failures

    # MBPP+ format: direct assertion statements
    if assertion_str:
        # Indent assertion statements for try block
        indented_assertions = "\n".join("    " + line for line in assertion_str.strip().split("\n"))
        full_test = f"""
{code}

import sys
try:
{indented_assertions}
except AssertionError as e:
    print(f"ASSERTION_FAILED: {{e}}", file=sys.stderr)
    sys.exit(1)
except TypeError as e:
    print(f"TYPE_ERROR: {{e}}", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"RUNTIME_ERROR: {{type(e).__name__}}: {{e}}", file=sys.stderr)
    sys.exit(1)
"""
        result = _run_test_code(full_test, timeout)
        if result:
            failures.add(result)
            return failures

    return failures


def _run_test_code(test_code: str, timeout: int) -> str:
    """Execute test code and return failure type or None."""
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_code)
            f.flush()
            temp_path = f.name

        result = subprocess.run(
            [sys.executable, temp_path],
            capture_output=True, text=True, timeout=timeout
        )
        Path(temp_path).unlink(missing_ok=True)

        if result.returncode != 0:
            stderr = result.stderr
            if "ASSERTION_FAILED" in stderr or "AssertionError" in stderr:
                return "exec:wrong_answer"
            elif "TYPE_ERROR" in stderr or "TypeError" in stderr:
                return "exec:runtime_error"
            elif "RUNTIME_ERROR" in stderr:
                return "exec:runtime_error"
            else:
                return "exec:runtime_error"

        return None

    except subprocess.TimeoutExpired:
        try:
            Path(temp_path).unlink(missing_ok=True)
        except:
            pass
        return "exec:timeout"
    except Exception:
        return "exec:runtime_error"
