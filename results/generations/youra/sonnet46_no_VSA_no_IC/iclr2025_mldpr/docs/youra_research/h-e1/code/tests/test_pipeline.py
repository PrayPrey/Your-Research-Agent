"""Spec compliance tests for pipeline.py."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import pytest
from pipeline import ols_detrend, run_pelt_changepoint


def make_synthetic(n=50, seed=0):
    rng = np.random.default_rng(seed)
    pc = rng.integers(5, 200, size=n).astype(float)
    cov = 0.5 - 0.001 * pc + rng.normal(0, 0.1, size=n)
    return pc, cov


def test_ols_detrend_returns_sorted():
    pc, cov = make_synthetic()
    sorted_pc, residuals, metrics = ols_detrend(pc, cov)
    assert np.all(np.diff(sorted_pc) >= 0), "sorted_paper_counts must be non-decreasing"


def test_ols_detrend_residuals_shape():
    pc, cov = make_synthetic()
    sorted_pc, residuals, metrics = ols_detrend(pc, cov)
    assert sorted_pc.shape == (len(pc),)
    assert residuals.shape == (len(pc),)


def test_ols_detrend_metrics_keys():
    pc, cov = make_synthetic()
    _, _, metrics = ols_detrend(pc, cov)
    for key in ("slope", "intercept", "rho", "r2", "p_value"):
        assert key in metrics


def test_ols_detrend_insufficient_data():
    with pytest.raises(ValueError, match="Insufficient"):
        ols_detrend(np.array([1.0]), np.array([0.5]))


def test_ols_detrend_zero_variance():
    pc = np.array([1.0, 2.0, 3.0])
    cov = np.array([0.5, 0.5, 0.5])
    with pytest.raises(ValueError, match="Zero variance"):
        ols_detrend(pc, cov)


def test_pelt_changepoint_returns_dict_keys():
    pc, cov = make_synthetic(n=60)
    result = run_pelt_changepoint(pc, cov)
    for key in ("paper_count_star", "breakpoint_idx", "pen_used", "n_bkps",
                "residual_cov_sorted", "sorted_paper_counts", "bkps_list",
                "pen_values", "ols_metrics"):
        assert key in result, f"Missing key: {key}"


def test_pelt_changepoint_shapes():
    n = 60
    pc, cov = make_synthetic(n=n)
    result = run_pelt_changepoint(pc, cov)
    assert result["residual_cov_sorted"].shape == (n,)
    assert result["sorted_paper_counts"].shape == (n,)
    assert len(result["pen_values"]) == 20


def test_pelt_changepoint_with_clear_break():
    """Synthetic signal with obvious break should detect breakpoint."""
    rng = np.random.default_rng(42)
    n = 80
    pc = np.arange(1, n + 1, dtype=float)
    # High CoV for pc < 40, low CoV for pc >= 40
    cov = np.where(pc < 40, 0.8, 0.2) + rng.normal(0, 0.05, size=n)
    result = run_pelt_changepoint(pc, cov)
    assert result["n_bkps"] >= 1, "Expected at least one breakpoint in synthetic signal"
    assert result["paper_count_star"] is not None
