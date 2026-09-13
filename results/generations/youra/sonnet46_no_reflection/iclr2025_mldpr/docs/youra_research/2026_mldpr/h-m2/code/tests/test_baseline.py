"""Tests for task-004: baseline.py spec compliance."""
import pytest
import numpy as np
import pandas as pd


def _make_panel():
    rows = []
    base = pd.Timestamp("2020-01-01")
    for b in range(10):
        for m in range(15):
            for q in range(10):
                date = base + pd.DateOffset(months=q * 3)
                rows.append({
                    "benchmark": f"bench_{b}",
                    "domain": "cv",
                    "model": f"model_{m}",
                    "date": date,
                    "score": float(np.random.rand()),
                    "quarter": date.to_period("Q").strftime("%YQ%q"),
                    "label": "saturated" if b < 5 else "healthy",
                })
    return pd.DataFrame(rows)


def test_extract_naive_features_columns():
    from baseline import extract_naive_features
    panel = _make_panel()
    result = extract_naive_features(panel)
    assert isinstance(result, pd.DataFrame)
    assert "benchmark" in result.columns
    assert "label" in result.columns
    # At least one feature column
    feature_cols = [c for c in result.columns if c not in ("benchmark", "label")]
    assert len(feature_cols) >= 1


def test_fit_baseline_returns_model():
    from baseline import fit_baseline
    X = np.random.rand(20, 3)
    y = np.array([1] * 10 + [0] * 10)
    model = fit_baseline(X, y)
    assert model is not None
    assert hasattr(model, "predict_proba")


def test_predict_baseline_probabilities_in_range():
    from baseline import fit_baseline, predict_baseline
    X = np.random.rand(20, 3)
    y = np.array([1] * 10 + [0] * 10)
    model = fit_baseline(X, y)
    probs = predict_baseline(model, X)
    assert probs.shape == (20,)
    assert np.all(probs >= 0.0)
    assert np.all(probs <= 1.0)
