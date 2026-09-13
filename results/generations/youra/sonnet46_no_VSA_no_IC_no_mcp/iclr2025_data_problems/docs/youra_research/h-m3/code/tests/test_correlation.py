"""Tests for correlation.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import pytest
from correlation import pearson_spearman, bootstrap_ci, directional_check, CorrelationResult

BENCHMARKS = ["mmlu", "hellaswag", "arc_challenge", "winogrande"]


def test_pearson_spearman_perfect_positive():
    x = np.array([1.0, 2.0, 3.0, 4.0] * 4)
    y = x * 2.0
    res = pearson_spearman(x, y)
    assert res.pearson_r > 0.999
    assert res.spearman_rho > 0.999
    assert res.n_observations == 16


def test_pearson_spearman_perfect_negative():
    x = np.array([1.0, 2.0, 3.0, 4.0] * 4)
    y = -x
    res = pearson_spearman(x, y)
    assert res.pearson_r < -0.999


def test_pearson_spearman_nan_raises():
    x = np.array([1.0, float("nan"), 3.0, 4.0])
    y = np.array([1.0, 2.0, 3.0, 4.0])
    with pytest.raises(ValueError, match="NaN"):
        pearson_spearman(x, y)


def test_pearson_spearman_length_mismatch():
    x = np.array([1.0, 2.0, 3.0])
    y = np.array([1.0, 2.0])
    with pytest.raises(ValueError, match="length mismatch"):
        pearson_spearman(x, y)


def test_bootstrap_ci_contains_observed():
    rng = np.random.default_rng(0)
    x = rng.uniform(0, 1, 16)
    y = x * 0.8 + rng.normal(0, 0.1, 16)
    res = pearson_spearman(x, y)
    (ci_lo, ci_hi), boot = bootstrap_ci(x, y, n_resamples=500, seed=42)
    assert ci_lo < res.pearson_r < ci_hi or abs(ci_lo - res.pearson_r) < 0.05
    assert len(boot) == 500


def test_bootstrap_ci_deterministic():
    rng = np.random.default_rng(1)
    x = rng.uniform(0, 1, 16)
    y = x + rng.normal(0, 0.2, 16)
    ci1, _ = bootstrap_ci(x, y, seed=42)
    ci2, _ = bootstrap_ci(x, y, seed=42)
    assert ci1 == ci2


def test_directional_check_structure():
    cont_vec = np.array([0.05, 0.20, 0.08, 0.025])  # winogrande<mmlu<arc<hellaswag
    diff_matrix = np.array([
        [-0.01, 0.02, 0.01, 0.005],
        [-0.01, 0.01, 0.01, 0.001],
        [-0.01, 0.02, 0.02, 0.01],
        [-0.01, 0.03, 0.01, 0.003],
    ])
    result = directional_check(cont_vec, diff_matrix)
    assert "n_correct_direction" in result
    assert "benchmark_signs" in result
    assert set(result["benchmark_signs"].keys()) == set(BENCHMARKS)
    assert 0.0 <= result["n_correct_direction"] <= 1.0


def test_correlation_result_to_dict():
    res = CorrelationResult(0.7, 0.01, 0.65, 0.02, 16, (0.5, 0.85))
    d = res.to_dict()
    assert d["pearson_r"] == 0.7
    assert d["bootstrap_ci_95"] == [0.5, 0.85]
