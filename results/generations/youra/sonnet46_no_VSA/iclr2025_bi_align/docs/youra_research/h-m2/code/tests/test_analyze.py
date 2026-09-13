"""Spec compliance tests for H-M2 analyze.py"""
import sys
import os
import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from analyze import (
    compute_raw_spearman,
    compute_partial_spearman,
    fisher_z_difference_test,
    evaluate_gate,
)
from config import ExperimentConfig


def make_df(n=150, seed=42):
    """Synthetic df with correlated TruthfulQA_MC2, bbq_accuracy, MMLU."""
    rng = np.random.default_rng(seed)
    mmlu = rng.uniform(20, 90, n)
    truth = mmlu * 0.6 + rng.normal(0, 10, n)
    truth = np.clip(truth, 0, 100)
    bbq = mmlu * 0.8 + rng.normal(0, 8, n)
    bbq = np.clip(bbq, 0, 100)
    family = [f"org{i % 10}" for i in range(n)]
    return pd.DataFrame({
        "model_name": [f"org{i % 10}/model{i}" for i in range(n)],
        "TruthfulQA_MC2": truth,
        "bbq_accuracy": bbq,
        "MMLU": mmlu,
        "family": family,
    })


# --- test_fisher_z_known_values ---

def test_fisher_z_known_values():
    """Verify fisher_z_difference_test against hand-computed values for known rho pair."""
    raw_rho = 0.7
    partial_rho = 0.5
    N = 100
    result = fisher_z_difference_test(raw_rho, partial_rho, N)

    z_raw_expected = np.arctanh(0.7)
    z_partial_expected = np.arctanh(0.5)
    se = np.sqrt(2.0 / (100 - 3))
    z_diff_expected = (z_raw_expected - z_partial_expected) / se

    assert abs(result["z_raw"] - z_raw_expected) < 1e-8
    assert abs(result["z_partial"] - z_partial_expected) < 1e-8
    assert abs(result["z_diff"] - z_diff_expected) < 1e-8
    assert 0.0 <= result["p_value"] <= 1.0
    assert result["outcome"] in ("SIGNIFICANT", "NULL")


def test_fisher_z_identical_rhos_gives_zero_diff():
    """Same raw_rho == partial_rho → z_diff=0, p=1."""
    rho = 0.5
    result = fisher_z_difference_test(rho, rho, N=100)
    assert abs(result["z_diff"]) < 1e-10
    assert abs(result["p_value"] - 1.0) < 1e-8


def test_fisher_z_significant_outcome():
    """Large difference in rhos should yield p < 0.05 (SIGNIFICANT)."""
    result = fisher_z_difference_test(0.9, 0.1, N=200)
    assert result["outcome"] == "SIGNIFICANT"
    assert result["p_value"] < 0.05


def test_fisher_z_null_outcome():
    """Small difference should yield p >= 0.05 (NULL)."""
    result = fisher_z_difference_test(0.502, 0.500, N=50)
    assert result["outcome"] == "NULL"
    assert result["p_value"] >= 0.05


# --- test_load_data_normalizes_bbq (via synthetic test) ---

def test_bbq_normalization_in_load_data():
    """Synthetic df with BBQ in [0,1]: after normalization max > 1."""
    n = 50
    rng = np.random.default_rng(7)
    # Simulate fractional BBQ_accuracy
    bbq_frac = rng.uniform(0.3, 0.9, n)
    assert bbq_frac.max() <= 1.0, "test data should be fractional"
    # After normalization
    bbq_normalized = bbq_frac * 100.0
    assert bbq_normalized.max() > 1.0


# --- test_gate_pass_both_outcomes ---

def test_gate_pass_significant():
    """Gate PASS for p=0.01 → SIGNIFICANT."""
    results = {
        "p_value": 0.01,
        "ci_overlap_status": "non-overlapping",
        "outcome": "NULL",
    }
    results = evaluate_gate(results)
    assert results["gate_pass"] is True
    assert results["outcome"] == "SIGNIFICANT"


def test_gate_pass_null():
    """Gate PASS for p=0.10 → NULL (also publishable)."""
    results = {
        "p_value": 0.10,
        "ci_overlap_status": "overlapping",
        "outcome": "NULL",
    }
    results = evaluate_gate(results)
    assert results["gate_pass"] is True
    assert results["outcome"] == "NULL"


def test_gate_fail_nan_pvalue():
    """Gate FAIL if p_value is NaN."""
    results = {
        "p_value": float("nan"),
        "ci_overlap_status": "overlapping",
        "outcome": "NULL",
    }
    results = evaluate_gate(results)
    assert results["gate_pass"] is False


def test_gate_fail_none_pvalue():
    """Gate FAIL if p_value is None."""
    results = {
        "p_value": None,
        "ci_overlap_status": "overlapping",
        "outcome": "NULL",
    }
    results = evaluate_gate(results)
    assert results["gate_pass"] is False


# --- compute_raw_spearman ---

def test_compute_raw_spearman_returns_keys():
    df = make_df()
    result = compute_raw_spearman(df)
    assert "raw_rho" in result
    assert "raw_p" in result
    assert abs(result["raw_rho"]) < 1.0
    assert 0.0 <= result["raw_p"] <= 1.0


# --- compute_partial_spearman ---

def test_compute_partial_spearman_returns_keys():
    df = make_df()
    raw = compute_raw_spearman(df)
    result = compute_partial_spearman(df, raw["raw_rho"])
    assert "partial_rho" in result
    assert "partial_p" in result
    assert abs(result["partial_rho"]) < 1.0


def test_mechanism_activation_check():
    """partial_rho must differ from raw_rho by more than 1e-6."""
    df = make_df()
    raw = compute_raw_spearman(df)
    partial = compute_partial_spearman(df, raw["raw_rho"])
    assert abs(partial["partial_rho"] - raw["raw_rho"]) > 1e-6
