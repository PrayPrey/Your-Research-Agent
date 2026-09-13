"""Tests for lgbm_trainer.py."""
import sys
import os
import pytest
import numpy as np

_CODE = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, os.path.abspath(_CODE))

from lgbm_trainer import run_cv_lgbm, compute_orbit_preds, decompose_mse


@pytest.fixture
def mock_data():
    rng = np.random.default_rng(0)
    N, K, D = 100, 50, 64
    X = rng.standard_normal((N, D)).astype(np.float32)
    y = rng.uniform(0.3, 0.95, N).astype(np.float64)
    permuted_X = rng.standard_normal((N, K, D)).astype(np.float32)
    return X, y, permuted_X


def test_run_cv_lgbm_fold_preds_shape(mock_data):
    X, y, _ = mock_data
    fold_preds, full_model = run_cv_lgbm(X, y, n_splits=5)
    assert fold_preds.shape == (100,), f"Expected (100,), got {fold_preds.shape}"


def test_run_cv_lgbm_full_model_fitted(mock_data):
    X, y, _ = mock_data
    _, full_model = run_cv_lgbm(X, y, n_splits=5)
    preds = full_model.predict(X)
    assert preds.shape == (100,)


def test_compute_orbit_preds_shape(mock_data):
    X, y, permuted_X = mock_data
    _, full_model = run_cv_lgbm(X, y, n_splits=5)
    orbit_preds = compute_orbit_preds(full_model, permuted_X)
    assert orbit_preds.shape == (100, 50), f"Expected (100, 50), got {orbit_preds.shape}"
    assert orbit_preds.dtype == np.float64


def test_decompose_mse_ratio_in_unit_interval(mock_data):
    X, y, permuted_X = mock_data
    fold_preds, full_model = run_cv_lgbm(X, y, n_splits=5)
    orbit_preds = compute_orbit_preds(full_model, permuted_X)
    results = decompose_mse(y, fold_preds, orbit_preds)
    assert results["ratio"] >= 0.0
    assert results["mse_perm"] > 0
    assert results["orbit_preds"].shape == (100, 50)
    assert results["per_model_orbit_var"].shape == (100,)
