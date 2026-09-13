"""Tests for evaluate.py."""
import sys
import os
import pytest
import numpy as np

_CODE = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, os.path.abspath(_CODE))

from evaluate import verify_mechanism, gate_check


@pytest.fixture
def valid_orbit_preds():
    rng = np.random.default_rng(42)
    return rng.standard_normal((100, 50)).astype(np.float64)


def test_verify_mechanism_passes(valid_orbit_preds):
    mse_total = 0.01
    mse_perm = 0.002
    ratio = mse_perm / mse_total
    indicators = verify_mechanism(valid_orbit_preds, mse_total, mse_perm, ratio)
    assert indicators["orbit_preds_shape_valid"]
    assert indicators["nonzero_orbit_variance"]
    assert indicators["mse_perm_positive"]
    assert indicators["ratio_computed"]


def test_verify_mechanism_wrong_shape():
    bad_preds = np.random.randn(50, 50)
    with pytest.raises(AssertionError):
        verify_mechanism(bad_preds, 0.01, 0.002, 0.2)


def test_gate_check_pass():
    results = {"ratio": 0.15, "mse_total": 0.01, "mse_perm": 0.0015,
               "mse_res": 0.0085, "r2_c1": 0.8, "tau_c1": 0.6}
    assert gate_check(results) is True


def test_gate_check_fail():
    results = {"ratio": 0.05, "mse_total": 0.01, "mse_perm": 0.0005,
               "mse_res": 0.0095, "r2_c1": 0.8, "tau_c1": 0.6}
    assert gate_check(results) is False
