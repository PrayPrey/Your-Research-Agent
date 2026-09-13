"""Tests for contract_checker module."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from contract_checker import exec_with_timeout, check_program_contract


def test_exec_with_timeout_success():
    code = "def add(a, b):\n    return a + b\n"
    func, err = exec_with_timeout(code, "add", timeout=5)
    assert func is not None, f"Expected callable, got error: {err}"
    assert err is None
    assert func(1, 2) == 3


def test_exec_with_timeout_missing_entry():
    code = "def foo():\n    pass\n"
    func, err = exec_with_timeout(code, "bar", timeout=5)
    assert func is None
    assert "not found" in err


def test_exec_with_timeout_syntax_error():
    code = "def bad(:\n    pass\n"
    func, err = exec_with_timeout(code, "bad", timeout=5)
    assert func is None
    assert err is not None


def test_check_program_contract_gap_detected():
    # Code with no contract checks — accepts any input silently
    code = "def f(x):\n    return x * 2\n"
    # CVT input: x must be positive integer (precondition), but code accepts x=0
    cvt_inputs = [{"input": {"x": -1}}, {"input": {"x": 0}}]
    result = check_program_contract(code, "f", cvt_inputs, timeout=5)
    # Code doesn't raise AssertionError → gap detected (n_failures > 0)
    assert result["n_total"] == 2
    assert result["n_failures"] == 2
    assert result["violated"] is True
    assert result["gap"] == 1.0


def test_check_program_contract_no_gap():
    # Code WITH contract enforcement (raises AssertionError on CVT inputs)
    code = "def f(x):\n    assert x > 0, 'must be positive'\n    return x * 2\n"
    cvt_inputs = [{"input": {"x": -1}}, {"input": {"x": 0}}]
    result = check_program_contract(code, "f", cvt_inputs, timeout=5)
    # Code raises AssertionError → no gap
    assert result["n_total"] == 2
    assert result["n_failures"] == 0
    assert result["violated"] is False
    assert result["gap"] == 0.0


def test_check_program_contract_exec_error():
    # Invalid code
    code = "not valid python !!!"
    cvt_inputs = [{"input": {"x": 1}}]
    result = check_program_contract(code, "f", cvt_inputs, timeout=5)
    assert result["violated"] is False
    assert result["error"] is not None
