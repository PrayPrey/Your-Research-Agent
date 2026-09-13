"""Spec compliance tests for fitting.py (H-E1)."""
import numpy as np
import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fitting import logistic, fit_linear, fit_logistic, _r2_aic


def make_logistic_data(n=80, K=0.92, r=0.4, t0=18.0, noise=0.02):
    """Generate synthetic S-curve data."""
    t = np.linspace(1, 54, n)
    y = K / (1 + np.exp(-r * (t - t0))) + np.random.default_rng(42).normal(0, noise, n)
    y = np.clip(y, 0, 1)
    return t, y


class TestLogisticKernel:
    def test_output_shape(self):
        t = np.linspace(0, 50, 100)
        out = logistic(t, K=0.9, r=0.5, t0=20.0)
        assert out.shape == (100,)

    def test_asymptote(self):
        t_large = np.array([1000.0])
        val = logistic(t_large, K=0.9, r=0.5, t0=20.0)
        assert abs(val[0] - 0.9) < 1e-6

    def test_inflection_at_t0(self):
        t = np.array([20.0])
        val = logistic(t, K=0.9, r=0.5, t0=20.0)
        assert abs(val[0] - 0.45) < 1e-6  # K/2

    def test_no_overflow(self):
        t = np.array([-1e6, 1e6])
        out = logistic(t, K=1.0, r=1.0, t0=0.0)
        assert np.all(np.isfinite(out))


class TestFitLinear:
    def test_returns_dict(self):
        t, y = np.linspace(0, 50, 60), np.linspace(0.2, 0.9, 60)
        result = fit_linear(t, y)
        assert isinstance(result, dict)
        assert set(result.keys()) == {"coeffs", "r2", "aic"}

    def test_coeffs_shape(self):
        t, y = np.linspace(0, 50, 60), np.linspace(0.2, 0.9, 60)
        result = fit_linear(t, y)
        assert result["coeffs"].shape == (2,)

    def test_r2_perfect_linear(self):
        t = np.linspace(0, 50, 100)
        y = 0.01 * t + 0.1
        result = fit_linear(t, y)
        assert result["r2"] > 0.999

    def test_r2_bounded(self):
        t, y = make_logistic_data()
        result = fit_linear(t, y)
        assert -1 <= result["r2"] <= 1


class TestFitLogistic:
    def test_returns_required_keys(self):
        t, y = make_logistic_data()
        result = fit_logistic(t, y)
        required = {"popt", "pcov", "r2", "aic", "ci95", "converged"}
        assert required.issubset(set(result.keys()))

    def test_popt_shape(self):
        t, y = make_logistic_data()
        result = fit_logistic(t, y)
        assert result["popt"].shape == (3,)

    def test_pcov_shape(self):
        t, y = make_logistic_data()
        result = fit_logistic(t, y)
        assert result["pcov"].shape == (3, 3)

    def test_ci95_shape(self):
        t, y = make_logistic_data()
        result = fit_logistic(t, y)
        assert result["ci95"].shape == (3,)

    def test_converges_on_clean_data(self):
        t, y = make_logistic_data(n=100, noise=0.01)
        result = fit_logistic(t, y)
        assert result["converged"] is True

    def test_r2_exceeds_threshold_on_clean(self):
        t, y = make_logistic_data(n=100, noise=0.01)
        result = fit_logistic(t, y)
        assert result["r2"] > 0.9

    def test_no_raise_on_degenerate(self):
        # Should NOT raise even if convergence fails
        t = np.linspace(0, 5, 10)
        y = np.zeros(10)  # degenerate data
        result = fit_logistic(t, y)
        assert isinstance(result["converged"], bool)


class TestR2AicHelper:
    def test_perfect_fit(self):
        y = np.array([0.1, 0.5, 0.9])
        r2, aic = _r2_aic(y, y, k=3)
        assert r2 == pytest.approx(1.0) or r2 > 0.99
