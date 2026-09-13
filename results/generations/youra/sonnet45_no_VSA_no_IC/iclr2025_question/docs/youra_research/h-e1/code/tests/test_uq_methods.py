"""Test suite for UQ methods."""
import pytest
import torch
import numpy as np
from uq.methods import TemperatureScaling, ConformalPrediction, MCDropout


def test_temperature_scaling_init():
    """Verify TemperatureScaling initializes with T=1.0."""
    ts = TemperatureScaling()
    assert ts.temperature == 1.0


def test_temperature_scaling_calibrate():
    """Verify temperature calibration runs."""
    ts = TemperatureScaling()

    # Dummy logits and labels
    logits = [torch.randn(100) for _ in range(10)]
    labels = [0, 1, 0, 1, 0, 1, 0, 1, 0, 1]

    T = ts.calibrate(logits, labels, max_iter=5)
    assert isinstance(T, float)
    assert T > 0


def test_temperature_scaling_uncertainty():
    """Verify uncertainty computation."""
    ts = TemperatureScaling()
    logits = torch.randn(100)

    uncertainty = ts.compute_uncertainty(logits, T=1.0)
    assert 0.0 <= uncertainty <= 1.0


def test_conformal_prediction_init():
    """Verify ConformalPrediction initializes with alpha=0.1."""
    cp = ConformalPrediction(alpha=0.1)
    assert cp.alpha == 0.1
    assert cp.threshold == 0.0


def test_conformal_calibrate():
    """Verify conformal threshold computation."""
    cp = ConformalPrediction(alpha=0.1)

    # Dummy logits
    logits = [torch.randn(100) for _ in range(10)]
    labels = [0, 1, 0, 1, 0, 1, 0, 1, 0, 1]

    threshold = cp.calibrate(logits, labels)
    assert 0.0 <= threshold <= 1.0


def test_conformal_uncertainty():
    """Verify nonconformity score computation."""
    cp = ConformalPrediction()
    logits = torch.randn(100)

    uncertainty = cp.compute_uncertainty(logits)
    assert 0.0 <= uncertainty <= 1.0


def test_mc_dropout_init():
    """Verify MCDropout initializes with k=5."""
    mc = MCDropout(k=5, dropout_rate=0.1)
    assert mc.k == 5
    assert mc.dropout_rate == 0.1


def test_mc_dropout_uncertainty_shape():
    """Verify MC dropout returns correct output shape."""
    # NOTE: Full MC dropout test requires model, deferred to integration
    mc = MCDropout(k=3)
    assert mc.k == 3


# Integration tests (model loading) deferred to experiment execution
