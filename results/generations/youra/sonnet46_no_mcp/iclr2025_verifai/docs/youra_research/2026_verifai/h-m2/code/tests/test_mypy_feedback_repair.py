import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mypy_feedback_repair import MypyFeedbackRepair
from config import MypyRepairConfig


def make_repair():
    return MypyFeedbackRepair(MypyRepairConfig())


def test_parse_mypy_output_empty():
    r = make_repair()
    assert r.parse_mypy_output("") == []


def test_parse_mypy_output_basic():
    r = make_repair()
    stdout = "/tmp/x.py:5: error: Argument 1 to 'foo' has incompatible type\n"
    errors = r.parse_mypy_output(stdout)
    assert len(errors) == 1
    assert errors[0] == (5, "error", "Argument 1 to 'foo' has incompatible type")


def test_parse_mypy_output_notes_ignored():
    r = make_repair()
    stdout = "/tmp/x.py:3: note: See https://mypy.readthedocs.io\n/tmp/x.py:3: error: Something wrong\n"
    errors = r.parse_mypy_output(stdout)
    assert len(errors) == 1


def test_format_structured_feedback_ast_error():
    r = make_repair()
    fb = r.format_structured_feedback(False, "unexpected indent (line 2)", [])
    assert "AST ERROR" in fb
    assert "unexpected indent" in fb


def test_format_structured_feedback_no_errors():
    r = make_repair()
    fb = r.format_structured_feedback(True, None, [])
    assert "No errors" in fb


def test_format_structured_feedback_mypy_errors():
    r = make_repair()
    errors = [(5, "error", "Incompatible return value type")]
    fb = r.format_structured_feedback(True, None, errors)
    assert "Type errors" in fb
    assert "Line 5" in fb


def test_format_structured_feedback_truncates_at_10():
    r = make_repair()
    errors = [(i, "error", f"Error {i}") for i in range(15)]
    fb = r.format_structured_feedback(True, None, errors)
    # Should only show first 10 errors
    lines_with_line = [l for l in fb.split("\n") if "Line" in l]
    assert len(lines_with_line) == 10


def test_build_repair_prompt_format():
    r = make_repair()
    prompt = r.build_repair_prompt("Compute sum of list", "def f(x): return x", "No errors.")
    assert "Compute sum of list" in prompt
    assert "def f(x): return x" in prompt
    assert "No errors." in prompt
    assert "Fixed code" in prompt


def test_build_repair_prompt_empty_problem():
    r = make_repair()
    prompt = r.build_repair_prompt("", "code here", "feedback here")
    assert "code here" in prompt
    assert "feedback here" in prompt


def test_compute_mechanism_activated_rate_all_zero():
    r = make_repair()
    pool = {"A": [{"rounds_used": 0}, {"rounds_used": 0}]}
    rate = r.compute_mechanism_activated_rate(pool)
    assert rate == 0.0


def test_compute_mechanism_activated_rate_some():
    r = make_repair()
    pool = {"A": [{"rounds_used": 1}, {"rounds_used": 0}], "B": [{"rounds_used": 2}]}
    rate = r.compute_mechanism_activated_rate(pool)
    assert abs(rate - 2/3) < 1e-9


def test_compute_mechanism_activated_rate_empty():
    r = make_repair()
    assert r.compute_mechanism_activated_rate({}) == 0.0
