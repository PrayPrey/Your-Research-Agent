"""Code execution sandbox with timeout."""

import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import List

@dataclass
class TestResult:
    passed: bool
    actual_output: str
    error: str = ""

def execute_code(code: str, test_input: str, expected_output: str, timeout: int = 5) -> TestResult:
    """Execute Python code against one test case."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        code_path = f.name

    try:
        result = subprocess.run(
            ['python3', code_path],
            input=test_input,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        actual = result.stdout.strip()
        expected = expected_output.strip()

        if result.returncode != 0:
            return TestResult(passed=False, actual_output=actual, error=result.stderr)

        return TestResult(passed=(actual == expected), actual_output=actual)

    except subprocess.TimeoutExpired:
        return TestResult(passed=False, actual_output="", error="Timeout")
    except Exception as e:
        return TestResult(passed=False, actual_output="", error=str(e))
    finally:
        Path(code_path).unlink(missing_ok=True)

def run_all_tests(code: str, test_cases: List) -> List[TestResult]:
    """Run code against all test cases."""
    results = []
    for tc in test_cases:
        result = execute_code(code, tc.input, tc.expected_output)
        results.append(result)
    return results
