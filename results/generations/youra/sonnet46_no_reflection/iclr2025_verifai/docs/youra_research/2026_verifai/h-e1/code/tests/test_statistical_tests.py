"""Tests for statistical_tests.py — spec compliance."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
import json
from evaluation.statistical_tests import (
    GateResult,
    one_sided_ttest_ls_a_gt_p,
    evaluate_gate,
    log_gate_result,
    write_results_json,
)


def test_gate_result_fields():
    g = GateResult(
        condition_a_mean=0.5,
        condition_b_mean=0.3,
        condition_p_mean=0.25,
        t_stat=2.0,
        p_value=0.02,
        gate_pass=True,
        secondary_pass=True,
    )
    assert g.gate_pass is True
    assert g.p_value == 0.02


def test_one_sided_ttest_pass():
    """LS_A clearly > LS_P should produce gate_pass=True."""
    ls_a = [0.6, 0.65, 0.7, 0.62, 0.68, 0.72, 0.58, 0.66]
    ls_p = [0.25, 0.22, 0.28, 0.24, 0.26, 0.23, 0.27, 0.25]
    result = one_sided_ttest_ls_a_gt_p(ls_a, ls_p)
    assert result.gate_pass is True
    assert result.p_value < 0.05
    assert result.condition_a_mean > result.condition_p_mean


def test_one_sided_ttest_fail():
    """LS_A ≈ LS_P should produce gate_pass=False."""
    ls_a = [0.25, 0.24, 0.26, 0.25, 0.24, 0.26, 0.25, 0.25]
    ls_p = [0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25]
    result = one_sided_ttest_ls_a_gt_p(ls_a, ls_p)
    assert result.gate_pass is False


def test_evaluate_gate():
    ls_by_condition = {
        "A": [0.6, 0.65, 0.7, 0.62, 0.68, 0.72, 0.58, 0.66],
        "B": [0.35, 0.38, 0.32, 0.36, 0.34, 0.37, 0.33, 0.36],
        "P": [0.25, 0.22, 0.28, 0.24, 0.26, 0.23, 0.27, 0.25],
    }
    result = evaluate_gate(ls_by_condition, "miniF2F")
    assert isinstance(result, GateResult)
    assert result.condition_b_mean > 0


def test_log_gate_result_format(capsys):
    result = GateResult(
        condition_a_mean=0.62,
        condition_b_mean=0.35,
        condition_p_mean=0.25,
        t_stat=3.5,
        p_value=0.003,
        gate_pass=True,
        secondary_pass=True,
    )
    log_gate_result(result, "miniF2F")
    captured = capsys.readouterr()
    assert "[H-E1] Locality Score" in captured.out
    assert "Condition A:" in captured.out
    assert "[H-E1] Gate Check:" in captured.out
    assert "LS_A > LS_P" in captured.out


def test_write_results_json(tmp_path):
    results = {
        "ls_minif2f": {"A": [0.6, 0.7], "B": [0.3, 0.4], "P": [0.25, 0.26]},
    }
    out = str(tmp_path / "results.json")
    write_results_json(results, out)
    assert os.path.exists(out)
    with open(out) as f:
        data = json.load(f)
    assert "ls_minif2f" in data
