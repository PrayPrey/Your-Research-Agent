"""Tests for evaluate.py: bootstrap CI, delta_rho, tier analysis, gate check."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import pytest
from evaluate import (bootstrap_spearman_ci, compute_delta_rho_ci,
                       compute_tier_analysis, check_hm3_gate)


def _synthetic_data(n=200, seed=0):
    rng = np.random.default_rng(seed)
    labels = rng.uniform(0.5, 0.99, n)
    flat_preds = labels + rng.normal(0, 0.1, n)
    nfn_preds  = labels + rng.normal(0, 0.04, n)
    ds_preds   = labels + rng.normal(0, 0.07, n)
    return labels, flat_preds, nfn_preds, ds_preds


def test_bootstrap_spearman_ci_reproducible():
    labels, flat_preds, _, _ = _synthetic_data()
    r1 = bootstrap_spearman_ci(labels, flat_preds, n_resamples=200, seed=42)
    r2 = bootstrap_spearman_ci(labels, flat_preds, n_resamples=200, seed=42)
    assert r1 == r2, "Results should be reproducible with same seed"
    median_rho, ci_lower, ci_upper = r1
    assert ci_lower <= median_rho <= ci_upper


def test_compute_delta_rho_ci_paired_bootstrap():
    labels, flat_preds, nfn_preds, _ = _synthetic_data()
    delta_rho, ci_lower, ci_upper = compute_delta_rho_ci(
        nfn_preds, flat_preds, labels, n_resamples=200, seed=42
    )
    assert ci_lower <= delta_rho <= ci_upper or abs(delta_rho - ci_lower) < 0.01
    # NFN has less noise so delta should be positive
    assert delta_rho > 0


def test_compute_tier_analysis_tercile_partition():
    labels, flat_preds, nfn_preds, ds_preds = _synthetic_data(n=300)
    result = compute_tier_analysis(flat_preds, nfn_preds, ds_preds, labels)
    assert set(result.keys()) >= {"low", "mid", "high", "low_n", "mid_n", "high_n"}
    total = result["low_n"] + result["mid_n"] + result["high_n"]
    assert total == 300


def test_check_hm3_gate_p1_p2():
    # Construct results that should pass both gates
    results = {
        "encoders": {
            "flat_mlp":  {"mnist_cnn": {"rho": 0.50}, "cifar10": {"rho": 0.45}},
            "deep_sets": {"mnist_cnn": {"rho": 0.60}, "cifar10": {"rho": 0.55}},
            "nfn":       {"mnist_cnn": {"rho": 0.68}, "cifar10": {"rho": 0.62}},
        },
        "delta_metrics": {
            "delta_rho_mnist": 0.18,
            "ci_lower_mnist":  0.05,
            "ci_upper_mnist":  0.30,
            "delta_rho_cifar": 0.17,
            "ci_lower_cifar":  0.04,
            "ci_upper_cifar":  0.29,
        },
    }
    p1, p2 = check_hm3_gate(results)
    assert p1 is True
    assert p2 is True

    # Test failing gate
    results["delta_metrics"]["delta_rho_mnist"] = 0.03
    p1_fail, _ = check_hm3_gate(results)
    assert p1_fail is False
