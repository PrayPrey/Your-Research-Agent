"""Tests for analyze_correlation module."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import pandas as pd
import pytest
from analyze_correlation import (
    bootstrap_rho_ci,
    kruskal_wallis_tiers,
    spearman_with_permutation,
    tier_means,
)


def _make_richness_df(n=20):
    rng = np.random.default_rng(0)
    tiers = rng.integers(1, 5, size=n)
    scores = tiers * 2.0 + rng.uniform(0, 1, size=n)
    return pd.DataFrame({
        "task_id": [f"t{i}" for i in range(n)],
        "tier": tiers.tolist(),
        "score": scores.tolist(),
        "has_quantifier": [False] * n,
        "has_relational": [False] * n,
        "node_count": tiers.tolist(),
    })


def _make_gap_dict(richness_df):
    # Positive correlation: higher score → higher gap
    rng = np.random.default_rng(1)
    return {row["task_id"]: row["score"] * 0.05 + rng.uniform(0, 0.1)
            for _, row in richness_df.iterrows()}


def test_spearman_positive_correlation():
    x = list(range(50))
    y = [v + 0.1 * i for i, v in enumerate(range(50))]
    result = spearman_with_permutation(x, y, n_resamples=99, seed=42)
    assert result["rho"] > 0.9
    assert result["p_asymptotic"] < 0.05


def test_spearman_returns_keys():
    x = list(range(10))
    y = list(range(10))
    result = spearman_with_permutation(x, y, n_resamples=99, seed=0)
    assert set(result.keys()) == {"rho", "p_asymptotic", "p_exact"}


def test_bootstrap_rho_ci_returns_tuple():
    x = list(range(30))
    y = list(range(30))
    lo, hi = bootstrap_rho_ci(x, y, n_bootstrap=100, seed=0)
    assert lo <= hi
    assert 0.8 < lo  # should be near 1


def test_kruskal_wallis_tiers():
    richness_df = _make_richness_df(40)
    gap_dict = _make_gap_dict(richness_df)
    kw_stat, kw_p = kruskal_wallis_tiers(richness_df, gap_dict)
    assert not np.isnan(kw_stat)


def test_tier_means_returns_four_tiers():
    richness_df = pd.DataFrame({
        "task_id": [f"t{i}" for i in range(4)],
        "tier": [1, 2, 3, 4],
        "score": [1.0, 2.0, 3.0, 4.0],
        "has_quantifier": [False] * 4,
        "has_relational": [False] * 4,
        "node_count": [1, 2, 3, 4],
    })
    gap_dict = {f"t{i}": float(i) * 0.1 for i in range(4)}
    means = tier_means(richness_df, gap_dict)
    assert set(means.keys()) == {1, 2, 3, 4}
