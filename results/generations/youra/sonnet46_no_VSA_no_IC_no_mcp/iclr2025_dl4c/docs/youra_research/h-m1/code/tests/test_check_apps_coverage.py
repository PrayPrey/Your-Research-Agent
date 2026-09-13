"""Tests for check_apps_coverage.py"""
import json
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from check_apps_coverage import check_solution_passes


def test_check_solution_passes_timeout():
    """Returns False on TimeoutExpired (infinite loop)."""
    infinite_loop = "while True: pass"
    result = check_solution_passes(infinite_loop, [{"input": "", "output": ""}], timeout=0.5)
    assert result is False


def test_check_solution_passes_wrong_output():
    """Returns False on wrong output."""
    wrong_soln = "print('wrong')"
    result = check_solution_passes(wrong_soln, [{"input": "", "output": "correct"}], timeout=5.0)
    assert result is False


def test_check_solution_passes_correct():
    """Returns True when solution passes all test cases."""
    soln = "print('hello')"
    result = check_solution_passes(soln, [{"input": "", "output": "hello"}], timeout=5.0)
    assert result is True


def test_check_solution_passes_crash():
    """Returns False on non-zero exit (syntax error)."""
    crash_soln = "raise ValueError('boom')"
    result = check_solution_passes(crash_soln, [{"input": "", "output": ""}], timeout=5.0)
    assert result is False


def test_compute_coverage_output_schema(tmp_path):
    """Output JSON has difficulty/total/solvable/coverage_pct."""
    from unittest.mock import patch
    from check_apps_coverage import compute_coverage

    output_path = str(tmp_path / "coverage.json")
    # Minimal fake dataset: 2 competition problems, 1 solvable
    fake_ds = [
        {
            "difficulty": "competition",
            "solutions": json.dumps(["print('yes')"]),
            "input_output": json.dumps({"inputs": [""], "outputs": ["yes"]}),
        },
        {
            "difficulty": "competition",
            "solutions": json.dumps(["print('wrong')"]),
            "input_output": json.dumps({"inputs": [""], "outputs": ["correct"]}),
        },
    ]
    with patch("check_apps_coverage.load_dataset", return_value=fake_ds):
        result = compute_coverage(output_path=output_path, max_problems=None)

    assert "difficulty" in result
    assert "total" in result
    assert "solvable" in result
    assert "coverage_pct" in result
    assert result["total"] == 2

    with open(output_path) as f:
        saved = json.load(f)
    assert "coverage_pct" in saved
