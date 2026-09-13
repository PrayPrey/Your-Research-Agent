"""Sandboxed test execution with timeout and majority voting."""
from dataclasses import dataclass
import subprocess
import tempfile
import os
from typing import Optional
from data import Problem
from config import ExperimentConfig


@dataclass
class ExecResult:
    passed: bool
    stdout: str
    stderr: str
    traceback: Optional[str]


def run_tests(code: str, problem: Problem, timeout_s: int) -> ExecResult:
    """Run tests for a problem in sandbox with timeout."""
    if problem.source == "humaneval":
        # HumanEval: code + test block
        full_code = code + "\n" + problem.tests
    else:
        # MBPP: code + test assertions
        full_code = code + "\n" + problem.tests

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(full_code)
        f.flush()
        temp_path = f.name

    try:
        result = subprocess.run(
            ["python", temp_path],
            capture_output=True,
            text=True,
            timeout=timeout_s,
            cwd=tempfile.gettempdir(),
        )
        passed = result.returncode == 0
        traceback = result.stderr if not passed else None
        return ExecResult(passed=passed, stdout=result.stdout, stderr=result.stderr, traceback=traceback)
    except subprocess.TimeoutExpired:
        return ExecResult(passed=False, stdout="", stderr="Timeout", traceback="TimeoutError: execution exceeded limit")
    except Exception as e:
        return ExecResult(passed=False, stdout="", stderr=str(e), traceback=str(e))
    finally:
        os.unlink(temp_path)


def run_tests_majority_vote(code: str, problem: Problem, cfg: ExperimentConfig) -> ExecResult:
    """Run tests multiple times and return majority vote result."""
    results = []
    for _ in range(cfg.exec_retries):
        result = run_tests(code, problem, cfg.exec_timeout_s)
        results.append(result)

    passed_count = sum(1 for r in results if r.passed)
    majority_passed = passed_count > cfg.exec_retries // 2

    # Return the first matching result for consistent stderr/stdout
    for r in results:
        if r.passed == majority_passed:
            return r
    return results[0]
