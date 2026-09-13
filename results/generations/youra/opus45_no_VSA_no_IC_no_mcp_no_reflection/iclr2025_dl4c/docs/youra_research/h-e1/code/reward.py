"""Reward engine with sandboxed code execution and multi-signal rewards."""
import subprocess
import sys
import tempfile
import re
from dataclasses import dataclass
from typing import Any, Optional

from config import ERROR_CATEGORY_SCORES, HIGH_BANDWIDTH_WEIGHTS


@dataclass
class TestResult:
    passed: bool
    error_type: str
    expected: Optional[Any] = None
    actual: Optional[Any] = None


def _classify_error(error_text: str) -> str:
    if "SyntaxError" in error_text or "IndentationError" in error_text:
        return "syntax_error"
    if "AssertionError" in error_text:
        return "assertion_error"
    return "runtime_error"


def _extract_expected_actual(error_text: str) -> tuple[Optional[Any], Optional[Any]]:
    match = re.search(r"AssertionError.*?(\d+\.?\d*).*?(\d+\.?\d*)", error_text)
    if match:
        try:
            return float(match.group(1)), float(match.group(2))
        except ValueError:
            pass
    return None, None


def execute_tests(code: str, test_cases: list[str], timeout: float = 5.0) -> list[TestResult]:
    results = []
    for test in test_cases:
        full_code = code + "\n" + test
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(full_code)
            f.flush()
            try:
                result = subprocess.run(
                    [sys.executable, f.name],
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
                if result.returncode == 0:
                    results.append(TestResult(passed=True, error_type="passed"))
                else:
                    error_type = _classify_error(result.stderr)
                    expected, actual = _extract_expected_actual(result.stderr)
                    results.append(TestResult(
                        passed=False, error_type=error_type,
                        expected=expected, actual=actual
                    ))
            except subprocess.TimeoutExpired:
                results.append(TestResult(passed=False, error_type="runtime_error"))
            except Exception:
                results.append(TestResult(passed=False, error_type="runtime_error"))
    return results


def _pass_ratio(results: list[TestResult]) -> float:
    if not results:
        return 0.0
    return sum(1 for r in results if r.passed) / len(results)


def _partial_credit(results: list[TestResult]) -> float:
    credits = []
    for r in results:
        if not r.passed and r.expected is not None and r.actual is not None:
            try:
                credits.append(1.0 / (1.0 + abs(float(r.expected) - float(r.actual))))
            except (ValueError, TypeError):
                pass
    return sum(credits) / len(credits) if credits else 0.0


def compute_reward(code: str, test_cases: list[str], condition: str) -> float:
    results = execute_tests(code, test_cases)

    if condition == "binary":
        return 1.0 if all(r.passed for r in results) else 0.0

    if condition == "categorical":
        if all(r.passed for r in results):
            return 1.0
        worst = min(
            ERROR_CATEGORY_SCORES.get(r.error_type, 0.0)
            for r in results if not r.passed
        )
        return worst

    if condition == "high_bandwidth":
        cat_score = compute_reward(code, test_cases, "categorical")
        ratio = _pass_ratio(results)
        partial = _partial_credit(results)
        w_cat, w_ratio, w_partial = HIGH_BANDWIDTH_WEIGHTS
        return w_cat * cat_score + w_ratio * ratio + w_partial * partial

    return 0.0
