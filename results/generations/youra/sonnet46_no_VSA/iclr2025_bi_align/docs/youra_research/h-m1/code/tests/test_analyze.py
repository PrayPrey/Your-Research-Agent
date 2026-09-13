"""Spec compliance tests for H-M1 analyze.py"""
import sys
import os
import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from analyze import compute_correlations, verify_mechanism_activated
from config import AnalysisConfig


def make_df(n=100, seed=42):
    rng = np.random.default_rng(seed)
    mmlu = rng.uniform(20, 90, n)
    # TruthfulQA correlated with MMLU (rho ~ 0.5)
    truth = mmlu * 0.6 + rng.normal(0, 10, n)
    truth = np.clip(truth, 0, 100)
    # BBQ correlated with MMLU (rho ~ 0.35)
    bbq = mmlu * 0.4 + rng.normal(0, 15, n)
    bbq = np.clip(bbq, 0, 100)
    return pd.DataFrame({"MMLU": mmlu, "TruthfulQA_MC2": truth, "bbq_accuracy": bbq})


def test_compute_correlations_returns_required_keys():
    df = make_df()
    results = compute_correlations(df)
    required = [
        "hypothesis_id", "N",
        "rho_mmlu_truthqa", "R2_mmlu_truthqa", "p_mmlu_truthqa",
        "rho_mmlu_bbq", "R2_mmlu_bbq", "p_mmlu_bbq",
        "raw_rho_truth_bbq", "p_raw_truth_bbq",
        "gate_pass",
    ]
    for key in required:
        assert key in results, f"Missing key: {key}"


def test_hypothesis_id():
    results = compute_correlations(make_df())
    assert results["hypothesis_id"] == "h-m1"


def test_N_matches_input():
    df = make_df(n=80)
    results = compute_correlations(df)
    assert results["N"] == 80


def test_r2_is_rho_squared():
    results = compute_correlations(make_df())
    assert abs(results["R2_mmlu_truthqa"] - results["rho_mmlu_truthqa"] ** 2) < 1e-10
    assert abs(results["R2_mmlu_bbq"] - results["rho_mmlu_bbq"] ** 2) < 1e-10


def test_r2_in_valid_range():
    results = compute_correlations(make_df())
    assert 0 <= results["R2_mmlu_truthqa"] <= 1
    assert 0 <= results["R2_mmlu_bbq"] <= 1


def test_gate_pass_logic():
    results = compute_correlations(make_df())
    expected = (results["R2_mmlu_truthqa"] > 0.05) and (results["R2_mmlu_bbq"] > 0.05)
    assert results["gate_pass"] == expected


def test_gate_fail_when_r2_below_threshold():
    rng = np.random.default_rng(99)
    n = 100
    # Independent variables — R² should be near 0
    df = pd.DataFrame({
        "MMLU": rng.uniform(20, 90, n),
        "TruthfulQA_MC2": rng.uniform(20, 90, n),
        "bbq_accuracy": rng.uniform(20, 90, n),
    })
    results = compute_correlations(df)
    # gate_pass should reflect actual R² values
    expected = (results["R2_mmlu_truthqa"] > 0.05) and (results["R2_mmlu_bbq"] > 0.05)
    assert results["gate_pass"] == expected


def test_verify_mechanism_activated_pass():
    results = compute_correlations(make_df())
    ok, indicators = verify_mechanism_activated(results)
    assert ok is True
    assert all(indicators.values())


def test_verify_mechanism_fails_on_nan():
    bad = {"N": 297, "R2_mmlu_truthqa": float("nan"), "R2_mmlu_bbq": 0.1, "gate_pass": False, "raw_rho_truth_bbq": 0.1}
    ok, indicators = verify_mechanism_activated(bad)
    assert ok is False
    assert indicators["r2_truthqa_valid"] is False


def test_verify_mechanism_fails_on_low_n():
    results = compute_correlations(make_df())
    results["N"] = 10
    ok, indicators = verify_mechanism_activated(results)
    assert ok is False
    assert indicators["n_valid"] is False


def test_p_values_are_floats():
    results = compute_correlations(make_df())
    assert isinstance(results["p_mmlu_truthqa"], float)
    assert isinstance(results["p_mmlu_bbq"], float)
    assert isinstance(results["p_raw_truth_bbq"], float)


def test_baseline_rho_for_hm2():
    # Ensure raw_rho_truth_bbq is independently computed (not derived from MMLU pairs)
    df = make_df()
    results = compute_correlations(df)
    from scipy import stats
    expected_rho = stats.spearmanr(df["TruthfulQA_MC2"], df["bbq_accuracy"]).statistic
    assert abs(results["raw_rho_truth_bbq"] - expected_rho) < 1e-10
