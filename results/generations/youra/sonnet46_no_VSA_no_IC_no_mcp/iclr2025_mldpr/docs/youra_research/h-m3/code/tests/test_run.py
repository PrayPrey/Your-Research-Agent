"""Spec-compliance tests for H-M3 parameter extraction."""
import sys
from pathlib import Path
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from run import (
    logistic,
    extract_params,
    verify_mechanism_activated,
    check_plausibility,
    check_pcov_validity,
    bootstrap_ci,
    K_LO, K_HI, T0_LO, T0_HI, CI_T0_MAX,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def synthetic_glue():
    """Synthetic GLUE-like timeseries matching H-M2 parameters."""
    rng = np.random.default_rng(0)
    t = np.linspace(0, 60, 120)
    K_true, r_true, t0_true = 0.8955, 0.2017, -6.771
    y_clean = logistic(t, K_true, r_true, t0_true)
    y = y_clean + rng.normal(0, 0.005, size=len(t))
    y = np.clip(y, 0, 1)
    return t, y


@pytest.fixture
def synthetic_superglue():
    rng = np.random.default_rng(1)
    t = np.linspace(0, 55, 100)
    K_true, r_true, t0_true = 0.8858, 0.1578, -2.855
    y_clean = logistic(t, K_true, r_true, t0_true)
    y = y_clean + rng.normal(0, 0.005, size=len(t))
    y = np.clip(y, 0, 1)
    return t, y


# ---------------------------------------------------------------------------
# logistic()
# ---------------------------------------------------------------------------

def test_logistic_shape():
    t = np.linspace(0, 50, 200)
    y = logistic(t, 0.9, 0.2, 10)
    assert y.shape == (200,)


def test_logistic_asymptote():
    t = np.array([1000.0])
    y = logistic(t, 0.9, 0.2, 10)
    assert abs(y[0] - 0.9) < 1e-6


def test_logistic_no_overflow():
    # Should not raise on extreme t values
    t = np.array([-1000.0, 0.0, 1000.0])
    y = logistic(t, 0.9, 0.2, 10)
    assert np.all(np.isfinite(y))


# ---------------------------------------------------------------------------
# extract_params()
# ---------------------------------------------------------------------------

def test_extract_params_returns_keys(synthetic_glue):
    t, y = synthetic_glue
    result = extract_params(t, y, "glue")
    required_keys = {"K", "r", "t0_relative", "t0_absolute", "perr",
                     "ci_95", "pcov", "popt", "pcov_finite", "bootstrap_used"}
    assert required_keys.issubset(result.keys())


def test_extract_params_popt_shape(synthetic_glue):
    t, y = synthetic_glue
    result = extract_params(t, y, "glue")
    assert len(result["popt"]) == 3
    assert len(result["ci_95"]) == 3


def test_extract_params_K_range(synthetic_glue):
    t, y = synthetic_glue
    result = extract_params(t, y, "glue")
    assert 0.5 <= result["K"] <= 1.05


def test_extract_params_r_positive(synthetic_glue):
    t, y = synthetic_glue
    result = extract_params(t, y, "glue")
    assert result["r"] > 0


def test_extract_params_t0_absolute_computed(synthetic_glue):
    t, y = synthetic_glue
    result = extract_params(t, y, "glue")
    # t0_absolute = t0_relative + benchmark_release_month (0 for glue)
    assert abs(result["t0_absolute"] - result["t0_relative"]) < 1e-9


def test_extract_params_ci_positive(synthetic_glue):
    t, y = synthetic_glue
    result = extract_params(t, y, "glue")
    assert all(c > 0 for c in result["ci_95"])


# ---------------------------------------------------------------------------
# verify_mechanism_activated()
# ---------------------------------------------------------------------------

def test_verify_mechanism_activated_returns_bool(synthetic_glue):
    t, y = synthetic_glue
    params = extract_params(t, y, "glue")
    ok, indicators = verify_mechanism_activated(params)
    assert isinstance(ok, bool)
    assert isinstance(indicators, dict)


def test_verify_mechanism_indicator_keys(synthetic_glue):
    t, y = synthetic_glue
    params = extract_params(t, y, "glue")
    _, indicators = verify_mechanism_activated(params)
    expected = {"popt_shape_correct", "pcov_finite", "K_extracted",
                "r_extracted", "t0_extracted", "ci_computed"}
    assert expected.issubset(indicators.keys())


def test_verify_mechanism_activated_on_good_fit(synthetic_glue):
    t, y = synthetic_glue
    params = extract_params(t, y, "glue")
    ok, _ = verify_mechanism_activated(params)
    assert ok is True


# ---------------------------------------------------------------------------
# check_plausibility()
# ---------------------------------------------------------------------------

def test_plausibility_returns_flags(synthetic_glue):
    t, y = synthetic_glue
    params = extract_params(t, y, "glue")
    result = check_plausibility(params)
    required = {"K_in_range", "r_positive", "t0_in_range",
                "t0_in_relaxed", "ci_t0_narrow", "ci_t0_width",
                "all_primary_pass", "all_relaxed_pass"}
    assert required.issubset(result.keys())


def test_plausibility_K_flag(synthetic_glue):
    t, y = synthetic_glue
    params = extract_params(t, y, "glue")
    result = check_plausibility(params)
    # K from H-M2 is 0.8955, which is in [0.85, 1.0]
    assert result["K_in_range"] is True


def test_plausibility_r_flag(synthetic_glue):
    t, y = synthetic_glue
    params = extract_params(t, y, "glue")
    result = check_plausibility(params)
    assert result["r_positive"] is True


def test_plausibility_ci_width_computed(synthetic_glue):
    t, y = synthetic_glue
    params = extract_params(t, y, "glue")
    result = check_plausibility(params)
    assert result["ci_t0_width"] == pytest.approx(2.0 * params["ci_95"][2], rel=1e-6)


# ---------------------------------------------------------------------------
# check_pcov_validity()
# ---------------------------------------------------------------------------

def test_pcov_validity_on_valid_matrix(synthetic_glue):
    t, y = synthetic_glue
    params = extract_params(t, y, "glue")
    pcov = np.array(params["pcov"])
    result = check_pcov_validity(pcov)
    assert isinstance(result, bool)


def test_pcov_validity_detects_inf():
    bad_pcov = np.array([[1, 0, 0], [0, np.inf, 0], [0, 0, 1]])
    assert check_pcov_validity(bad_pcov) is False


def test_pcov_validity_passes_on_finite():
    good_pcov = np.eye(3) * 0.01
    assert check_pcov_validity(good_pcov) is True


# ---------------------------------------------------------------------------
# bootstrap_ci()
# ---------------------------------------------------------------------------

def test_bootstrap_ci_returns_shape(synthetic_glue):
    t, y = synthetic_glue
    params = extract_params(t, y, "glue")
    popt = np.array(params["popt"])
    perr, samples = bootstrap_ci(t, y, popt, n=50)
    assert perr.shape == (3,)


def test_bootstrap_ci_positive_std(synthetic_glue):
    t, y = synthetic_glue
    params = extract_params(t, y, "glue")
    popt = np.array(params["popt"])
    perr, _ = bootstrap_ci(t, y, popt, n=50)
    # All stds should be positive for well-identified parameters
    assert np.all(perr >= 0)


# ---------------------------------------------------------------------------
# Integration: both benchmarks pass mechanism activation
# ---------------------------------------------------------------------------

def test_integration_both_benchmarks(synthetic_glue, synthetic_superglue):
    """Both benchmarks must pass mechanism activation."""
    for bm_name, (t, y) in [("glue", synthetic_glue), ("superglue", synthetic_superglue)]:
        params = extract_params(t, y, bm_name)
        ok, _ = verify_mechanism_activated(params)
        assert ok is True, f"Mechanism activation failed for {bm_name}"
