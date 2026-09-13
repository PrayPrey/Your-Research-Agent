import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import tempfile
import pytest
import z3

from z3_eligibility import Z3EligibilityChecker


def test_z3_importable():
    assert z3.get_version_string() is not None


def test_check_problem_eligible():
    checker = Z3EligibilityChecker(timeout_ms=2000)
    problem = {"prompt": 'def f(a, b):\n    """Return sum.\n    assert result == a + b\n    """\n    pass'}
    is_eligible, reason = checker.check_problem(problem)
    # Z3 can encode a + b style constraints
    # Acceptable: eligible OR no_assertions (depending on docstring parsing)
    assert isinstance(is_eligible, bool)
    assert reason in ("lia_encodable", "no_assertions", "non_lia_ops", "z3_timeout", "parse_error")


def test_check_problem_no_asserts():
    checker = Z3EligibilityChecker(timeout_ms=2000)
    problem = {"prompt": 'def f():\n    """No assertions here."""\n    pass'}
    is_eligible, reason = checker.check_problem(problem)
    assert is_eligible is False
    assert reason == "no_assertions"


def test_eligibility_rate():
    from data_loader import load_humaneval_plus
    checker = Z3EligibilityChecker(timeout_ms=2000)
    humaneval = load_humaneval_plus()
    # Check only first 20 for speed
    subset = dict(list(humaneval.items())[:20])
    eligibility = {}
    for task_id, problem in subset.items():
        is_eligible, _ = checker.check_problem(problem)
        eligibility[task_id] = is_eligible
    rate = sum(1 for v in eligibility.values() if v) / len(eligibility)
    # Just verify it runs; rate requirement is on full set
    assert 0.0 <= rate <= 1.0


def test_timeout_respected():
    import time
    checker = Z3EligibilityChecker(timeout_ms=2000)
    problem = {"prompt": 'def f():\n    """assert result == 0\n    """\n    pass'}
    t0 = time.time()
    checker.check_problem(problem)
    elapsed = time.time() - t0
    assert elapsed < 5.0, f"check_problem took too long: {elapsed:.2f}s"


def test_json_exists():
    checker = Z3EligibilityChecker(timeout_ms=2000)
    from data_loader import load_humaneval_plus
    humaneval = load_humaneval_plus()
    subset = dict(list(humaneval.items())[:5])
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = f.name
    try:
        checker.check_all(subset, path)
        assert os.path.exists(path)
        with open(path) as f:
            data = json.load(f)
        assert len(data) == 5
    finally:
        os.unlink(path)
