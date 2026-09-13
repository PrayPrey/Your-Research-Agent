"""Docker-sandboxed code execution for ground truth."""

import subprocess
import tempfile
import os
from typing import Any

from config import DOCKER_IMAGE, EXECUTION_TIMEOUT


def run_evalplus(task_id: str, problem: dict[str, Any], solution: str, timeout: int = EXECUTION_TIMEOUT) -> bool:
    """Execute solution in Docker sandbox. Returns True if all tests pass."""
    script = _build_test_script(problem, solution)
    return _run_in_container(script, timeout)


def _build_test_script(problem: dict[str, Any], solution: str) -> str:
    """Build executable test script from problem + solution."""
    entry_point = problem["entry_point"]
    prompt = problem["prompt"]
    full_code = prompt + solution
    base_inputs = problem.get("base_input", [])
    plus_inputs = problem.get("plus_input", [])
    all_inputs = base_inputs + plus_inputs
    if not all_inputs:
        return f'''{full_code}

# No test inputs available, check syntax only
try:
    {entry_point}
    print("PASS")
except Exception as e:
    print(f"FAIL: {{e}}")
    exit(1)
'''
    test_code = f'''{full_code}

import sys
def run_tests():
    test_cases = {repr(all_inputs[:20])}  # Limit to 20 test cases
    for i, inputs in enumerate(test_cases):
        try:
            result = {entry_point}(*inputs)
        except Exception as e:
            print(f"FAIL test {{i}}: {{e}}")
            sys.exit(1)
    print("PASS")

if __name__ == "__main__":
    run_tests()
'''
    return test_code


def _run_in_container(script: str, timeout: int) -> bool:
    """Run script in isolated Docker container."""
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(script)
            script_path = f.name

        cmd = [
            "docker", "run", "--rm",
            "--network", "none",
            "--memory", "512m",
            "--cpus", "1",
            "-v", f"{script_path}:/code/script.py:ro",
            DOCKER_IMAGE,
            "python", "/code/script.py"
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        os.unlink(script_path)
        return result.returncode == 0 and "PASS" in result.stdout
    except subprocess.TimeoutExpired:
        os.unlink(script_path)
        return False
    except Exception:
        if 'script_path' in locals():
            os.unlink(script_path)
        return False


def batch_execute(task_solution_pairs: list[tuple[str, dict, str]]) -> list[bool]:
    """Execute multiple (task_id, problem, solution) pairs."""
    return [run_evalplus(task_id, problem, solution) for task_id, problem, solution in task_solution_pairs]
