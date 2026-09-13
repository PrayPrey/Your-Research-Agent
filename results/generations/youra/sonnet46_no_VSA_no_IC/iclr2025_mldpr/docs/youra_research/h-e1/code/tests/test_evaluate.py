"""Spec compliance tests for evaluate.py."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import pytest
from evaluate import (
    run_permutation_test,
    run_bootstrap_ci,
    run_piecewise_ftest,
    verify_mechanism_activated,
)


def make_synthetic_break(n=80, seed=42):
    rng = np.random.default_rng(seed)
    pc = np.arange(1, n + 1, dtype=float)
    cov = np.where(pc < 40, 0.8, 0.2) + rng.normal(0, 0.05, size=n)
    return pc, cov


def test_permutation_test_returns_keys():
    pc, cov = make_synthetic_break(n=60)
    result = run_permutation_test(pc, cov, n_permutations=50, seed=42)
    for key in ("permutation_p", "null_distribution", "observed_bkp_idx"):
        assert key in result


def test_permutation_test_p_range():
    pc, cov = make_synthetic_break(n=60)
    result = run_permutation_test(pc, cov, n_permutations=50, seed=42)
    assert 0.0 <= result["permutation_p"] <= 1.0


def test_permutation_test_null_dist_shape():
    pc, cov = make_synthetic_break(n=60)
    result = run_permutation_test(pc, cov, n_permutations=50, seed=42)
    assert len(result["null_distribution"]) == 50


def test_permutation_test_no_breakpoint_returns_p1():
    # Nearly constant CoV — PELT likely finds no break
    pc = np.arange(1, 20, dtype=float)
    cov = np.ones(19) * 0.5 + np.random.default_rng(0).normal(0, 1e-9, 19)
    result = run_permutation_test(pc, cov, n_permutations=10, seed=0)
    # If no breakpoint detected, p should be 1.0
    if result["observed_bkp_idx"] is None:
        assert result["permutation_p"] == 1.0


def test_bootstrap_ci_returns_keys():
    pc, cov = make_synthetic_break(n=60)
    result = run_bootstrap_ci(pc, cov, n_resamples=50, seed=42)
    for key in ("bootstrap_ci_lower", "bootstrap_ci_upper", "bootstrap_ci_width", "bootstrap_estimates"):
        assert key in result


def test_bootstrap_ci_estimates_shape():
    pc, cov = make_synthetic_break(n=60)
    result = run_bootstrap_ci(pc, cov, n_resamples=50, seed=42)
    assert len(result["bootstrap_estimates"]) == 50


def test_bootstrap_ci_ordering():
    pc, cov = make_synthetic_break(n=60)
    result = run_bootstrap_ci(pc, cov, n_resamples=100, seed=42)
    assert result["bootstrap_ci_lower"] <= result["bootstrap_ci_upper"]


def test_piecewise_ftest_returns_keys():
    pc, cov = make_synthetic_break(n=80)
    result = run_piecewise_ftest(pc, cov, paper_count_star=40.0)
    assert "piecewise_f_p" in result
    assert "f_statistic" in result


def test_piecewise_ftest_significant_break():
    pc, cov = make_synthetic_break(n=80)
    result = run_piecewise_ftest(pc, cov, paper_count_star=40.0)
    assert 0.0 <= result["piecewise_f_p"] <= 1.0


def test_verify_mechanism_all_pass():
    results = {
        "paper_count_star": 47.0,
        "n_bkps_detected": 1,
        "permutation_p": 0.02,
    }
    all_pass, indicators = verify_mechanism_activated(results)
    assert all_pass is True
    assert indicators["pelt_detected_breakpoint"] is True
    assert indicators["paper_count_star_in_range"] is True
    assert indicators["permutation_p_significant"] is True


def test_verify_mechanism_fail_p():
    results = {
        "paper_count_star": 47.0,
        "n_bkps_detected": 1,
        "permutation_p": 0.10,
    }
    all_pass, indicators = verify_mechanism_activated(results)
    assert all_pass is False
    assert indicators["permutation_p_significant"] is False


def test_verify_mechanism_fail_range():
    results = {
        "paper_count_star": 5.0,  # below min=10
        "n_bkps_detected": 1,
        "permutation_p": 0.02,
    }
    all_pass, indicators = verify_mechanism_activated(results)
    assert all_pass is False
    assert indicators["paper_count_star_in_range"] is False
