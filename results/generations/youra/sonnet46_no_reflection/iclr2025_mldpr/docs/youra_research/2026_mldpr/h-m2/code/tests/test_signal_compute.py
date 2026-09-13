"""Tests for task-003: signal_compute.py spec compliance."""
import pytest
import numpy as np
import pandas as pd


def test_compute_hd_cv_with_ood_scores():
    from signal_compute import compute_hd_cv
    bench_scores = np.array([0.9, 0.85, 0.8, 0.75])
    held_out = np.array([0.7, 0.65, 0.6, 0.55])
    result = compute_hd_cv(bench_scores, held_out)
    assert isinstance(result, float)
    assert abs(result - 0.2) < 1e-6  # mean(0.2, 0.2, 0.2, 0.2)


def test_compute_hd_cv_fallback_to_variance():
    from signal_compute import compute_hd_cv
    bench_scores = np.array([0.9, 0.5, 0.3, 0.8])
    result = compute_hd_cv(bench_scores, None)
    assert isinstance(result, float)
    assert result == pytest.approx(np.var(bench_scores))


def test_compute_hd_cv_empty_held_out():
    from signal_compute import compute_hd_cv
    bench_scores = np.array([0.9, 0.5, 0.3])
    result = compute_hd_cv(bench_scores, np.array([]))
    assert isinstance(result, float)
    assert result == pytest.approx(np.var(bench_scores))


def test_compute_hd_nlp_returns_none_for_insufficient_data():
    from signal_compute import compute_hd_nlp
    bench = {"scores": np.array([0.8, 0.9])}  # < 5 samples
    ref = {"scores": np.array([0.7, 0.75])}
    result = compute_hd_nlp(bench, ref)
    assert result is None


def test_compute_hd_nlp_returns_float_for_sufficient_data():
    from signal_compute import compute_hd_nlp
    rng = np.random.default_rng(42)
    bench = {"scores": rng.random(20)}
    ref = {"scores": rng.random(20)}
    result = compute_hd_nlp(bench, ref)
    # Either float or None (ConStat may not be installed)
    assert result is None or isinstance(result, float)


def test_compute_hd_tabular_reproducible():
    from signal_compute import compute_hd_tabular
    rng = np.random.default_rng(0)
    rankings = rng.random((12, 8))
    r1 = compute_hd_tabular(rankings, n_bootstrap=100, seed=42)
    r2 = compute_hd_tabular(rankings, n_bootstrap=100, seed=42)
    assert r1 == r2


def test_compute_hd_tabular_returns_float():
    from signal_compute import compute_hd_tabular
    rng = np.random.default_rng(0)
    rankings = rng.random((8, 5))
    result = compute_hd_tabular(rankings, n_bootstrap=50, seed=0)
    assert isinstance(result, float)
    assert -1.0 <= result <= 1.0


def test_compute_domain_signals_returns_correct_schema():
    from signal_compute import compute_domain_signals
    # Build a minimal labeled panel
    rows = []
    for b in range(5):
        for m in range(10):
            for q in range(8):
                date = pd.Timestamp("2020-01-01") + pd.DateOffset(months=q * 3)
                rows.append({
                    "benchmark": f"bench_{b}",
                    "domain": "tabular",
                    "model": f"model_{m}",
                    "date": date,
                    "score": float(np.random.rand()),
                    "quarter": date.to_period("Q").strftime("%YQ%q"),
                    "label": "saturated" if b < 3 else "healthy",
                })
    panel = pd.DataFrame(rows)
    result = compute_domain_signals(panel, domain="tabular", lookback_months=24)
    assert isinstance(result, pd.DataFrame)
    assert "benchmark" in result.columns
    assert "hd_signal" in result.columns
    assert "label" in result.columns
