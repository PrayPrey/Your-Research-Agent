import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import tempfile

from metrics import MetricsEvaluator


GOOD_CODE = "def f(a, b):\n    return a + b\n"
BAD_CODE = "def f(a b)\n    return a + b"  # Syntax error


def test_ast_failure_rate_good():
    ev = MetricsEvaluator()
    pool = {"t1": [GOOD_CODE, GOOD_CODE]}
    rate = ev.compute_ast_failure_rate(pool)
    assert rate == 0.0


def test_ast_failure_rate_bad():
    ev = MetricsEvaluator()
    pool = {"t1": [BAD_CODE, BAD_CODE]}
    rate = ev.compute_ast_failure_rate(pool)
    assert rate == 1.0


def test_delta_ast_direction():
    ev = MetricsEvaluator()
    # Baseline has more failures, syncode has fewer
    baseline = {"t1": [BAD_CODE, BAD_CODE], "t2": [BAD_CODE, GOOD_CODE]}
    syncode = {"t1": [GOOD_CODE, GOOD_CODE], "t2": [GOOD_CODE, GOOD_CODE]}
    delta = ev.compute_delta_ast(baseline, syncode)
    assert delta > 0, f"Expected delta > 0, got {delta}"


def test_z3_eligibility_rate():
    ev = MetricsEvaluator()
    eligibility = {"t1": True, "t2": False, "t3": True, "t4": True}
    rate = ev.compute_z3_eligibility_rate(eligibility)
    assert abs(rate - 0.75) < 1e-6


def test_mypy_structured_rate():
    ev = MetricsEvaluator()
    mypy_results = {
        "t1": {"exit_code": 0},
        "t2": {"exit_code": 1},
        "t3": {"exit_code": 0},
        "t4": {"exit_code": 2},  # Error
    }
    rate = ev.compute_mypy_structured_rate(mypy_results)
    assert abs(rate - 0.75) < 1e-6


def test_gate_evaluation_pass():
    ev = MetricsEvaluator()
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = f.name
    try:
        result = ev.evaluate_gate(0.1, 0.20, 0.95, path)
        assert result["gate_pass"] is True
        assert os.path.exists(path)
        with open(path) as f:
            data = json.load(f)
        assert "gate_pass" in data
    finally:
        os.unlink(path)


def test_gate_evaluation_fail():
    ev = MetricsEvaluator()
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = f.name
    try:
        result = ev.evaluate_gate(-0.05, 0.20, 0.95, path)
        assert result["gate_pass"] is False
    finally:
        os.unlink(path)
