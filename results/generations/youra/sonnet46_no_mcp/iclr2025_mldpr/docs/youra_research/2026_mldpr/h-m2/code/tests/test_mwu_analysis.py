"""Tests for mwu_analysis module."""
import pytest
import numpy as np
import pandas as pd
from src.mwu_analysis import compute_effect_size_r, run_mwu_unadjusted, run_mwu_matched, run_ols_standardized, run_mechanism_check


def test_compute_effect_size_r_bounds():
    # Perfect separation: U=0 → r=1
    assert compute_effect_size_r(0, 10, 10) == 1.0
    # U = n1*n2 → r = -1
    assert compute_effect_size_r(100, 10, 10) == -1.0


def test_compute_effect_size_r_zero_denom():
    assert compute_effect_size_r(5, 0, 0) == 0.0


def test_compute_effect_size_r_midpoint():
    # U = n1*n2/2 → r = 0
    assert abs(compute_effect_size_r(50, 10, 10)) < 1e-10


def test_run_mwu_unadjusted_returns_keys():
    df = pd.DataFrame({
        "high_accessible": [1]*50 + [0]*50,
        "run_count_12m": list(range(50, 100)) + list(range(50)),
    })
    result = run_mwu_unadjusted(df)
    assert "mwu_stat" in result
    assert "p_value" in result
    assert "n_high" in result
    assert "n_low" in result
    assert result["n_high"] == 50
    assert result["n_low"] == 50


def test_run_mwu_unadjusted_significant():
    rng = np.random.RandomState(42)
    df = pd.DataFrame({
        "high_accessible": [1]*100 + [0]*100,
        "run_count_12m": list(rng.poisson(20, 100)) + list(rng.poisson(5, 100)),
    })
    result = run_mwu_unadjusted(df)
    assert result["p_value"] < 0.05


def test_run_mwu_matched_direction_pass():
    df = pd.DataFrame({
        "high_accessible": [1]*30 + [0]*30,
        "run_count_12m": [10]*30 + [5]*30,
        "pair_id": list(range(30)) + list(range(30)),
    })
    result = run_mwu_matched(df)
    assert result["direction_pass"] is True
    assert result["effect_size_r"] != 0  # non-zero effect


def test_run_mwu_matched_empty():
    df = pd.DataFrame({"high_accessible": [], "run_count_12m": [], "pair_id": []})
    result = run_mwu_matched(df)
    assert result["p_value"] == 1.0
    assert result["direction_pass"] is False


def test_run_ols_standardized_basic():
    rng = np.random.RandomState(42)
    n = 100
    df = pd.DataFrame({
        "fair_A": rng.uniform(0, 1, n),
        "fair_F": rng.uniform(0, 1, n),
        "fair_I": rng.uniform(0, 1, n),
        "fair_R": rng.uniform(0, 1, n),
    })
    df["run_count_12m"] = df["fair_A"] * 10 + rng.normal(0, 1, n)
    result = run_ols_standardized(df, ["fair_F", "fair_A", "fair_I", "fair_R"])
    assert "accessible_beta" in result
    assert result["accessible_beta"] > 0  # fair_A drives run_count


def test_run_ols_standardized_no_cols():
    df = pd.DataFrame({"run_count_12m": [1, 2, 3]})
    result = run_ols_standardized(df, ["fair_A", "fair_F"])
    assert result["accessible_beta"] == 0.0


def test_run_mechanism_check_fails_on_few_pairs():
    results = {"n_matched_pairs": 5, "smd_max": 0.05, "high_mean": 10}
    checks = run_mechanism_check(results)
    assert checks["sufficient_pairs"] is False
    assert checks["all_pass"] is False


def test_run_mechanism_check_passes():
    results = {"n_matched_pairs": 100, "smd_max": 0.05, "high_mean": 10}
    checks = run_mechanism_check(results)
    assert checks["all_pass"] is True


def test_run_mechanism_check_smd_fail():
    results = {"n_matched_pairs": 100, "smd_max": 0.15, "high_mean": 10}
    checks = run_mechanism_check(results)
    assert checks["smd_ok"] is False
    assert checks["all_pass"] is False
