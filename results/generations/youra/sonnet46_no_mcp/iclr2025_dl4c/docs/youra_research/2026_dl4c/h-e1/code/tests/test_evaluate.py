"""Tests for evaluation/evaluate.py spec compliance."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from evaluation.evaluate import (
    parse_evalplus_output, run_mcnemar_test, gate_check, save_results
)
import tempfile, json


def test_parse_evalplus_output_json():
    stdout = '{"pass@1": 0.456, "base_tests": {"pass@1": 0.5}}'
    result = parse_evalplus_output(stdout)
    assert abs(result["pass@1"] - 0.456) < 1e-6


def test_parse_evalplus_output_multiline():
    stdout = "Loading model...\nRunning eval...\n{\"pass@1\": 0.312}"
    result = parse_evalplus_output(stdout)
    assert abs(result["pass@1"] - 0.312) < 1e-6


def test_parse_evalplus_output_regex_fallback():
    stdout = 'Results: "pass@1": 0.250 done'
    result = parse_evalplus_output(stdout)
    assert abs(result["pass@1"] - 0.250) < 1e-6


def test_parse_evalplus_output_invalid():
    with pytest.raises(ValueError):
        parse_evalplus_output("no json here at all")


def test_run_mcnemar_test_curriculum_better():
    # Curriculum passes 10 more problems
    n = 164
    curriculum = [True] * 90 + [False] * 74
    uniform = [True] * 80 + [False] * 84
    p_val, effect = run_mcnemar_test(curriculum, uniform)
    assert 0.0 <= p_val <= 1.0
    assert effect > 0  # curriculum better


def test_run_mcnemar_test_equal():
    results = [True, False] * 82
    p_val, effect = run_mcnemar_test(results, results)
    assert effect == 0.0


def test_run_mcnemar_test_length_mismatch():
    with pytest.raises(AssertionError):
        run_mcnemar_test([True, False], [True])


def test_gate_check_pass():
    assert gate_check(0.42, 0.39, 0.03) is True   # +3pp, p=0.03 < 0.05


def test_gate_check_fail_insufficient_gap():
    assert gate_check(0.41, 0.40, 0.03) is False   # only +1pp


def test_gate_check_fail_not_significant():
    assert gate_check(0.43, 0.40, 0.10) is False   # p=0.10 >= 0.05


def test_gate_check_fail_both():
    assert gate_check(0.40, 0.40, 0.10) is False


def test_save_results():
    with tempfile.TemporaryDirectory() as tmpdir:
        results = {"pass@1": 0.35, "condition": "curriculum"}
        save_results("curriculum", results, tmpdir)
        path = os.path.join(tmpdir, "eval_results_curriculum.json")
        assert os.path.exists(path)
        with open(path) as f:
            loaded = json.load(f)
        assert loaded["pass@1"] == 0.35
