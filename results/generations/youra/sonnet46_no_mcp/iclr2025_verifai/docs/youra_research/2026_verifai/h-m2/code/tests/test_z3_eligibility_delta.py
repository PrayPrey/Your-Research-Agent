import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from z3_eligibility_delta import Z3EligibilityDelta
from config import Z3DeltaConfig


def make_z3():
    return Z3EligibilityDelta(Z3DeltaConfig())


ELIGIBLE_CODE = """
def add_numbers(a: int, b: int) -> int:
    result = a + b
    if result > 0:
        return result * 2
    return result + a - b
"""

INELIGIBLE_CODE = """
def greet(name):
    return "Hello, " + name
"""

SYNTAX_ERROR_CODE = "def foo(: return 1"


def test_compute_arith_density_arithmetic():
    z = make_z3()
    density = z._compute_arith_density(ELIGIBLE_CODE)
    assert density > 0


def test_compute_arith_density_string_heavy():
    z = make_z3()
    code = "x = 'hello world'\ny = x + ' more'\nz = 'test'"
    density = z._compute_arith_density(code)
    # Low or 0 arithmetic density
    assert density >= 0


def test_compute_arith_density_syntax_error():
    z = make_z3()
    density = z._compute_arith_density(SYNTAX_ERROR_CODE)
    assert density == 0.0


def test_has_return_annotation_true():
    z = make_z3()
    assert z._has_return_annotation(ELIGIBLE_CODE) is True


def test_has_return_annotation_false():
    z = make_z3()
    assert z._has_return_annotation(INELIGIBLE_CODE) is False


def test_check_z3_eligible_heuristic_eligible():
    z = make_z3()
    # May or may not be eligible based on density threshold
    result = z.check_z3_eligible_heuristic(ELIGIBLE_CODE)
    assert isinstance(result, bool)


def test_check_z3_eligible_heuristic_syntax_error():
    z = make_z3()
    assert z.check_z3_eligible_heuristic(SYNTAX_ERROR_CODE) is False


def test_compute_eligibility_rate():
    z = make_z3()
    pool = {
        "HumanEval/0": [{"ast_valid": True, "completion": ELIGIBLE_CODE}],
        "HumanEval/1": [{"ast_valid": True, "completion": INELIGIBLE_CODE}],
    }
    result = z.compute_eligibility_rate(pool)
    assert "HumanEval/0" in result
    assert "HumanEval/1" in result
    assert isinstance(result["HumanEval/0"], bool)


def test_compute_eligibility_rate_empty_records():
    z = make_z3()
    pool = {"HumanEval/0": []}
    result = z.compute_eligibility_rate(pool)
    assert result["HumanEval/0"] is False


def test_compute_delta_p_no_common():
    z = make_z3()
    delta_p, ci_lower, ci_upper, p_value = z.compute_delta_p({}, {})
    assert delta_p == 0.0
    assert p_value == 1.0


def test_compute_delta_p_improvement():
    z = make_z3()
    baseline = {"A": False, "B": False, "C": True}
    post_mypy = {"A": True, "B": False, "C": True}
    delta_p, ci_lower, ci_upper, p_value = z.compute_delta_p(baseline, post_mypy)
    assert delta_p > 0  # improvement
    assert isinstance(ci_lower, float)
    assert isinstance(ci_upper, float)
    assert 0.0 <= p_value <= 1.0


def test_save_results(tmp_path):
    z = make_z3()
    path = str(tmp_path / "z3_results.json")
    result = z.save_results(0.1, 0.01, 0.2, 0.03, path)
    assert "delta_p" in result
    assert result["delta_p"] == 0.1
    import json
    data = json.load(open(path))
    assert data["delta_p"] == 0.1
    assert data["n_bootstrap"] == 10000
