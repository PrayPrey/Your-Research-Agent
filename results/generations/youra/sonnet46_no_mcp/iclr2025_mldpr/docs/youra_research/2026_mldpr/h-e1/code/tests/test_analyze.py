"""Tests for src/analyze.py (task-010, task-011)"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
import types
from src.analyze import (
    compute_cv,
    compute_group_sizes,
    compute_spearman_correlations,
    detect_bimodality,
    run_analysis,
    evaluate_gate,
)


def _make_cfg():
    return types.SimpleNamespace(
        FAIR_THRESHOLD=0.5,
        CV_GATE=0.15,
        GROUP_SIZE_GATE=500,
    )


def _make_scored(n=1000, seed=42):
    rng = np.random.default_rng(seed)
    scores = rng.uniform(0, 1, n)
    ordinals = rng.integers(700000, 740000, n)
    return pd.DataFrame({
        "did": range(n),
        "fair_aggregate": scores,
        "fair_F": scores,
        "fair_A": scores,
        "fair_I": scores,
        "fair_R": scores,
        "status": ["ok"] * n,
        "upload_date_ordinal": ordinals,
        "NumberOfInstances": rng.uniform(100, 10000, n),
        "NumberOfFeatures": rng.uniform(5, 100, n),
        "MajorityClassPercentage": rng.uniform(10, 90, n),
    })


def test_compute_cv_basic():
    s = pd.Series([0.1, 0.2, 0.3, 0.4, 0.5])
    cv = compute_cv(s)
    assert isinstance(cv, float)
    assert cv > 0


def test_compute_cv_empty():
    assert np.isnan(compute_cv(pd.Series([], dtype=float)))


def test_compute_cv_all_nan():
    assert np.isnan(compute_cv(pd.Series([np.nan, np.nan])))


def test_compute_group_sizes_sum():
    s = pd.Series(np.linspace(0, 1, 1000))
    n_high, n_low = compute_group_sizes(s, 0.5)
    assert n_high + n_low == 1000
    assert n_high > 0
    assert n_low > 0


def test_compute_group_sizes_threshold():
    s = pd.Series([0.0, 0.3, 0.5, 0.7, 1.0])
    n_high, n_low = compute_group_sizes(s, 0.5)
    assert n_high == 3  # 0.5, 0.7, 1.0
    assert n_low == 2   # 0.0, 0.3


def test_compute_spearman_correlations_basic():
    rng = np.random.default_rng(0)
    n = 100
    x = rng.uniform(0, 1, n)
    df = pd.DataFrame({"fair_aggregate": x, "covar": x + rng.normal(0, 0.01, n)})
    result = compute_spearman_correlations(df, "fair_aggregate", ["covar"])
    assert "covar" in result
    assert abs(result["covar"]) > 0.9  # strongly correlated


def test_compute_spearman_correlations_missing_col():
    df = pd.DataFrame({"fair_aggregate": [0.1, 0.2, 0.3]})
    result = compute_spearman_correlations(df, "fair_aggregate", ["nonexistent"])
    assert np.isnan(result["nonexistent"])


def test_detect_bimodality_returns_dict():
    s = pd.Series(np.random.uniform(0, 1, 200))
    result = detect_bimodality(s)
    assert "bimodal" in result
    assert "dip_stat" in result
    assert "dip_p" in result
    assert "bc" in result
    assert isinstance(result["bimodal"], bool)


def test_run_analysis_keys():
    scored = _make_scored(1000)
    cfg = _make_cfg()
    metrics = run_analysis(scored, cfg)
    expected_keys = ["cv", "n_high", "n_low", "r_quality", "r_date",
                     "bimodality", "mean_fair", "std_fair", "n_total", "n_failed"]
    for k in expected_keys:
        assert k in metrics, f"Missing key: {k}"


def test_run_analysis_cv_in_range():
    scored = _make_scored(1000)
    cfg = _make_cfg()
    metrics = run_analysis(scored, cfg)
    assert metrics["cv"] is not None
    assert metrics["cv"] > 0


def test_evaluate_gate_pass():
    cfg = _make_cfg()
    metrics = {"cv": 0.30, "n_high": 600, "n_low": 400}
    # n_low=400 < 500 → FAIL
    gate = evaluate_gate(metrics, cfg)
    assert gate["passed"] == False

    metrics2 = {"cv": 0.30, "n_high": 600, "n_low": 600}
    gate2 = evaluate_gate(metrics2, cfg)
    assert gate2["passed"] == True
    assert gate2["reason"] == "PASS"


def test_evaluate_gate_fail_cv():
    cfg = _make_cfg()
    metrics = {"cv": 0.10, "n_high": 600, "n_low": 600}
    gate = evaluate_gate(metrics, cfg)
    assert gate["passed"] == False
    assert "CV" in gate["reason"]


def test_evaluate_gate_reason_string():
    cfg = _make_cfg()
    metrics = {"cv": 0.05, "n_high": 100, "n_low": 100}
    gate = evaluate_gate(metrics, cfg)
    assert gate["passed"] == False
    assert isinstance(gate["reason"], str)
    assert len(gate["reason"]) > 0
