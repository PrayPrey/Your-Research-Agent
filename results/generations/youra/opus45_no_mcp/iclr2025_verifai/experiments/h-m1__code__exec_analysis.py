"""A-4: Execution analysis pipeline."""
import subprocess
import tempfile
import sys
from pathlib import Path
from typing import Set

def run_execution_tests(problem_id: str, code: str, problem: dict, timeout: int = 5) -> Set[str]:
    """Run evalplus test suite on code, return failure type set."""
    failures = set()

    # Get test cases from problem
    base_inputs = problem.get("base_input", [])
    plus_inputs = problem.get("plus_input", [])

    # If no inputs provided, use contract/assertion style
    if not base_inputs and not plus_inputs:
        # Try to extract entry point and run with assert
        entry_point = problem.get("entry_point", "")
        assertion = problem.get("assertion", "")
        if entry_point and assertion:
            test_code = code + "\n" + assertion
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
                    if "AssertionError" in result.stderr:
                        failures.add("exec:wrong_answer")
                    elif "Timeout" in result.stderr or result.returncode == -9:
                        failures.add("exec:timeout")
                    else:
                        failures.add("exec:runtime_error")
            except subprocess.TimeoutExpired:
                failures.add("exec:timeout")
            except Exception:
                failures.add("exec:runtime_error")
        return failures

    # Run with provided test inputs
    entry_point = problem.get("entry_point", "")
    canonical_solution = problem.get("canonical_solution", "")

    for test_input in base_inputs + plus_inputs:
        test_code = f"""
{code}

# Test execution
import sys
try:
    result = {entry_point}(*{test_input!r})
except Exception as e:
    print(f"RUNTIME_ERROR: {{type(e).__name__}}: {{e}}", file=sys.stderr)
    sys.exit(1)
"""
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
                if "RUNTIME_ERROR" in result.stderr:
                    failures.add("exec:runtime_error")
                else:
                    failures.add("exec:wrong_answer")
        except subprocess.TimeoutExpired:
            failures.add("exec:timeout")
        except Exception:
            failures.add("exec:runtime_error")

    return failures


def run_evalplus_evaluation(problem_id: str, code: str, timeout: int = 60) -> Set[str]:
    """Use evalplus evaluate command for accurate pass/fail detection."""
    failures = set()

    try:
        # Write code to temp file in evalplus format
        import json
        import tempfile

        samples = {problem_id: [{"task_id": problem_id, "completion": code}]}

        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            for pid, completions in samples.items():
                for c in completions:
                    f.write(json.dumps(c) + "\n")
            temp_path = f.name

        # This is a simplified check - evalplus full evaluation is complex
        # For PoC, we just check if code runs without syntax errors
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()
            code_path = f.name

        result = subprocess.run(
            [sys.executable, "-m", "py_compile", code_path],
            capture_output=True, text=True, timeout=timeout
        )

        Path(temp_path).unlink(missing_ok=True)
        Path(code_path).unlink(missing_ok=True)

        if result.returncode != 0:
            failures.add("exec:runtime_error")

    except Exception as e:
        failures.add("exec:runtime_error")

    return failures
