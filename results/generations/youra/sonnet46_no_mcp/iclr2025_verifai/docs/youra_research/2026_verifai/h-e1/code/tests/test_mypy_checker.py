import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import tempfile
import pytest
import mypy.api

from mypy_checker import MypyChecker


def test_mypy_importable():
    assert mypy.api is not None


def test_structured_output_valid_code():
    checker = MypyChecker()
    code = "x: int = 42\nprint(x)\n"
    stdout, stderr, exit_code = checker.check_code(code)
    assert exit_code in (0, 1), f"Unexpected exit code: {exit_code}"


def test_structured_output_type_error():
    checker = MypyChecker()
    code = "x: int = 'hello'\n"
    stdout, stderr, exit_code = checker.check_code(code)
    # mypy should return exit_code=1 for type error
    assert exit_code in (0, 1), f"Unexpected exit code: {exit_code}"


def test_parse_output():
    checker = MypyChecker()
    code = "x: int = 'hello'\n"
    stdout, stderr, exit_code = checker.check_code(code)
    parsed = checker.parse_output(stdout)
    assert isinstance(parsed, list)
    for item in parsed:
        assert "line" in item
        assert "message" in item


def test_rate():
    checker = MypyChecker()
    from data_loader import load_humaneval_plus
    humaneval = load_humaneval_plus()
    # Build a mini pool with simple code
    pool = {tid: [prob["prompt"] + "    pass\n"] for tid, prob in list(humaneval.items())[:20]}
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = f.name
    try:
        results = checker.check_pool(pool, path, sample_size=20)
        rate = sum(1 for r in results.values() if r["exit_code"] in (0, 1)) / len(results)
        assert rate >= 0.90, f"mypy_structured_rate {rate:.2%} < 0.90"
    finally:
        os.unlink(path)


def test_json_exists():
    checker = MypyChecker()
    pool = {"HumanEval/0": ["def add(a, b):\n    return a + b\n"]}
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = f.name
    try:
        checker.check_pool(pool, path, sample_size=1)
        assert os.path.exists(path)
    finally:
        os.unlink(path)
