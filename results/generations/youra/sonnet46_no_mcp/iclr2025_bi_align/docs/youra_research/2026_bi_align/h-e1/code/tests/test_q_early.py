"""Tests for q_early.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import pytest
from q_early import QEarlyModel


def make_data(n=500):
    rng = np.random.default_rng(42)
    X = rng.standard_normal((n, 3))
    y = (X[:, 0] + rng.standard_normal(n) * 0.5 > 0).astype(int)
    return X, y


def test_fit_predict():
    X, y = make_data()
    model = QEarlyModel()
    model.fit(X, y)
    proba = model.predict_proba(X)
    assert proba.shape == (len(X), 2)
    assert np.allclose(proba.sum(axis=1), 1.0, atol=1e-6)


def test_calibrate():
    X, y = make_data()
    model = QEarlyModel()
    model.fit(X[:300], y[:300])
    model.calibrate(X[300:], y[300:])
    proba = model.predict_proba(X)
    assert proba.shape == (len(X), 2)


def test_brier_score():
    X, y = make_data()
    model = QEarlyModel()
    model.fit(X, y)
    score = model.brier_score(X, y)
    assert 0.0 <= score <= 1.0


def test_gate_check_pass():
    model = QEarlyModel()
    assert model.gate_check(0.25, 0.26) is True


def test_gate_check_fail():
    model = QEarlyModel()
    with pytest.raises(RuntimeError, match="Brier gate FAILED"):
        model.gate_check(0.20, 0.25)


def test_predict_before_fit():
    model = QEarlyModel()
    X, _ = make_data(10)
    with pytest.raises(RuntimeError):
        model.predict_proba(X)
