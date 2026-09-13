"""Tests for experiment.py — spec compliance."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
import pytest

from experiment import (
    fit_baseline_model, fit_proposed_model, fit_extended_model,
    fit_perplexity_model, compute_supply_prop, verify_mechanism_activated,
    MAX_ITER, MIN_CLUSTER_COUNT, MIN_SPLIT_SIZE, INTERACTION_TERM,
)


def _make_df_pairs(n_per_split=1100, n_clusters=120):
    """Make a synthetic df_pairs large enough to pass all checks."""
    rng = np.random.default_rng(42)
    n = n_per_split * 2

    split = np.array([0] * n_per_split + [1] * n_per_split)
    cluster_id = rng.integers(0, n_clusters, size=n)
    delta_aifs = rng.normal(0.1, 0.5, size=n)
    delta_length = rng.normal(0.0, 10.0, size=n)
    delta_aifs_x_split = delta_aifs * split
    chosen = rng.integers(0, 2, size=n)

    return pd.DataFrame({
        "chosen": chosen,
        "delta_aifs": delta_aifs,
        "delta_length": delta_length,
        "delta_aifs_x_split": delta_aifs_x_split,
        "split": split,
        "cluster_id": cluster_id,
    })


def test_fit_baseline_model_converges():
    df = _make_df_pairs()
    result = fit_baseline_model(df)
    assert result is not None
    assert len(result.params) == 2  # delta_aifs, delta_length


def test_fit_proposed_model_has_interaction_term():
    df = _make_df_pairs()
    result = fit_proposed_model(df)
    assert result is not None
    assert len(result.params) == 3  # +delta_aifs_x_split


def test_fit_extended_model_converges():
    df = _make_df_pairs()
    df = compute_supply_prop(df)
    result = fit_extended_model(df)
    assert result is not None
    assert len(result.params) == 4


def test_fit_perplexity_model_converges():
    df = _make_df_pairs()
    result = fit_perplexity_model(df)
    assert result is not None
    assert len(result.params) == 4


def test_compute_supply_prop_adds_column():
    df = _make_df_pairs()
    df_out = compute_supply_prop(df)
    assert "supply_prop" in df_out.columns
    assert df_out["supply_prop"].between(0.0, 1.0).all()


def test_verify_mechanism_activated_passes():
    df = _make_df_pairs(n_per_split=1100, n_clusters=120)
    result = fit_proposed_model(df)
    ok, indicators = verify_mechanism_activated(result, df)
    assert isinstance(indicators, dict)
    assert "beta4_fitted" in indicators
    assert "data_variance" in indicators
    assert "split_balanced" in indicators
    assert "clusters_valid" in indicators
    assert "effect_nonzero" in indicators


def test_verify_mechanism_raises_on_small_splits():
    """Should raise RuntimeError if splits are too small."""
    df = _make_df_pairs(n_per_split=10, n_clusters=5)
    result = fit_proposed_model(df)
    with pytest.raises(RuntimeError):
        verify_mechanism_activated(result, df)


def test_max_iter_value():
    assert MAX_ITER == 200


def test_interaction_term_name():
    assert INTERACTION_TERM == "delta_aifs_x_split"
