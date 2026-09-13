"""Spec compliance tests for pipeline.py (H-E1)."""

import sys
import pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import pytest
from unittest.mock import MagicMock, patch


def test_extract_code_strips_fences():
    from pipeline import extract_code
    raw = "```python\ndef foo():\n    return 1\n```"
    result = extract_code(raw)
    assert result == "def foo():\n    return 1"


def test_extract_code_no_fences():
    from pipeline import extract_code
    raw = "def foo():\n    return 1"
    assert extract_code(raw) == raw.strip()


def test_build_prompt_contains_prompt():
    from pipeline import build_prompt
    problem = {"prompt": "def add(a, b):"}
    result = build_prompt(problem)
    assert "def add(a, b):" in result


def test_run_mypy_clean_code():
    from pipeline import run_mypy
    code = "x: int = 1\n"
    has_error, error_count, categories, stdout = run_mypy(code)
    assert isinstance(has_error, bool)
    assert isinstance(error_count, int)
    assert isinstance(categories, dict)


def test_run_mypy_type_error_code():
    from pipeline import run_mypy
    # Deliberately wrong type annotation
    code = 'x: int = "hello"\n'
    has_error, error_count, categories, stdout = run_mypy(code)
    # mypy should flag this
    assert has_error is True
    assert error_count >= 1


def test_run_mypy_returns_tuple_of_4():
    from pipeline import run_mypy
    result = run_mypy("pass\n")
    assert len(result) == 4


def test_extract_error_categories_parses_name_error():
    from pipeline import extract_error_categories
    stdout = 'foo.py:1: error: Name "bar" is not defined  [name-defined]\n'
    cats = extract_error_categories(stdout)
    assert cats["name-error"] >= 1


def test_extract_error_categories_empty():
    from pipeline import extract_error_categories
    cats = extract_error_categories("")
    assert all(v == 0 for v in cats.values())


def test_aggregate_basic():
    from pipeline import aggregate
    results = [
        {"task_id": "Mbpp/1", "seed": 42, "benchmark": "mbpp+", "passed": False, "has_mypy_error": True, "error_count": 2},
        {"task_id": "Mbpp/2", "seed": 42, "benchmark": "mbpp+", "passed": False, "has_mypy_error": False, "error_count": 0},
        {"task_id": "Mbpp/3", "seed": 42, "benchmark": "mbpp+", "passed": False, "has_mypy_error": True, "error_count": 1},
        {"task_id": "Mbpp/1", "seed": 123, "benchmark": "mbpp+", "passed": False, "has_mypy_error": True, "error_count": 1},
        {"task_id": "Mbpp/2", "seed": 123, "benchmark": "mbpp+", "passed": False, "has_mypy_error": False, "error_count": 0},
    ]
    summary = aggregate(results)
    assert "mbpp+" in summary
    assert "type_error_fraction_mean" in summary["mbpp+"]
    assert 0.0 <= summary["mbpp+"]["type_error_fraction_mean"] <= 1.0


def test_verify_mechanism_activated_true():
    from pipeline import verify_mechanism_activated
    results = [
        {"has_mypy_error": True, "error_count": 1},
        {"has_mypy_error": False, "error_count": 0},
    ] * 30  # 60 entries
    activated, indicators = verify_mechanism_activated(results)
    assert indicators["mypy_ran"] is True
    assert indicators["errors_found"] is True
    assert activated is True


def test_verify_mechanism_activated_no_errors():
    from pipeline import verify_mechanism_activated
    results = [{"has_mypy_error": False, "error_count": 0}] * 60
    activated, indicators = verify_mechanism_activated(results)
    assert indicators["errors_found"] is False
    assert activated is False


def test_load_problems_mbpp():
    from pipeline import load_problems
    problems = load_problems("mbpp+")
    assert len(problems) == 378
    # Each problem has a prompt
    for task_id, prob in list(problems.items())[:5]:
        assert "prompt" in prob


def test_load_problems_humaneval():
    from pipeline import load_problems
    problems = load_problems("humaneval+")
    assert len(problems) == 164
