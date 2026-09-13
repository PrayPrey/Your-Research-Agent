"""Tests for MSE decomposition correctness."""
import sys
import os
import numpy as np

_CODE = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, os.path.abspath(_CODE))

from lgbm_trainer import decompose_mse


def test_mse_decomp_orbit_preds_shape():
    rng = np.random.default_rng(1)
    N, K = 100, 50
    y = rng.uniform(0.3, 0.95, N)
    fold_preds = rng.uniform(0.3, 0.95, N)
    orbit_preds = rng.standard_normal((N, K)).astype(np.float64)
    results = decompose_mse(y, fold_preds, orbit_preds)
    assert results["orbit_preds"].shape == (N, K)


def test_mse_decomp_mse_perm_positive():
    rng = np.random.default_rng(2)
    N, K = 100, 50
    y = rng.uniform(0.3, 0.95, N)
    fold_preds = rng.uniform(0.3, 0.95, N)
    # orbit_preds with actual variation so mse_perm > 0
    orbit_preds = rng.standard_normal((N, K)).astype(np.float64)
    results = decompose_mse(y, fold_preds, orbit_preds)
    assert results["mse_perm"] > 0


def test_mse_decomp_ratio_nonnegative():
    rng = np.random.default_rng(3)
    N, K = 100, 50
    y = rng.uniform(0.3, 0.95, N)
    fold_preds = rng.uniform(0.3, 0.95, N)
    orbit_preds = rng.standard_normal((N, K)).astype(np.float64)
    results = decompose_mse(y, fold_preds, orbit_preds)
    assert results["ratio"] >= 0.0
