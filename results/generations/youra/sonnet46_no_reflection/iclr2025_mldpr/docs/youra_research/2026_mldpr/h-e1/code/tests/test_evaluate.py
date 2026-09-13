"""Tests for task-005: evaluate.py spec compliance."""
import pytest
import numpy as np
import pandas as pd


def _make_domain_signals(n_sat=20, n_healthy=20, domain="cv", sep=1.0):
    """Make domain signals DataFrame with clear separation."""
    rng = np.random.default_rng(42)
    sat = rng.normal(loc=sep, scale=0.3, size=n_sat)
    healthy = rng.normal(loc=0.0, scale=0.3, size=n_healthy)
    rows = (
        [{"benchmark": f"sat_{i}", "label": "saturated", "hd_signal": float(v), "domain": domain}
         for i, v in enumerate(sat)]
        + [{"benchmark": f"h_{i}", "label": "healthy", "hd_signal": float(v), "domain": domain}
           for i, v in enumerate(healthy)]
    )
    return pd.DataFrame(rows)


def test_test_discriminability_returns_dict():
    from evaluate import test_discriminability
    sat = np.array([0.8, 0.9, 0.85, 0.7, 0.95] * 4)
    healthy = np.array([0.3, 0.25, 0.35, 0.4, 0.28] * 4)
    result = test_discriminability(sat, healthy)
    assert isinstance(result, dict)
    for key in ("u_stat", "p_value", "cohens_d", "auc", "n_sat", "n_healthy"):
        assert key in result


def test_test_discriminability_separable_signals():
    from evaluate import test_discriminability
    sat = np.linspace(0.7, 1.0, 25)
    healthy = np.linspace(0.0, 0.3, 25)
    result = test_discriminability(sat, healthy)
    assert result["p_value"] < 0.05
    assert result["cohens_d"] > 0.5
    assert result["auc"] > 0.5


def test_check_gate_condition_pass():
    from evaluate import check_gate_condition
    domain_results = {
        "cv": {"discriminability": {"p_value": 0.01, "cohens_d": 0.8, "auc": 0.85,
                                    "n_sat": 20, "n_healthy": 20}},
        "nlp": {"discriminability": {"p_value": 0.02, "cohens_d": 0.7, "auc": 0.80,
                                     "n_sat": 20, "n_healthy": 20}},
        "tabular": {"discriminability": {"p_value": 0.3, "cohens_d": 0.2, "auc": 0.55,
                                         "n_sat": 20, "n_healthy": 20}},
    }
    passed, details = check_gate_condition(domain_results)
    assert passed is True


def test_check_gate_condition_fail():
    from evaluate import check_gate_condition
    domain_results = {
        "cv": {"discriminability": {"p_value": 0.2, "cohens_d": 0.1, "auc": 0.55,
                                    "n_sat": 10, "n_healthy": 10}},
        "nlp": {"discriminability": {"p_value": 0.4, "cohens_d": 0.15, "auc": 0.52,
                                     "n_sat": 10, "n_healthy": 10}},
        "tabular": {"discriminability": {"p_value": 0.5, "cohens_d": 0.05, "auc": 0.51,
                                         "n_sat": 10, "n_healthy": 10}},
    }
    passed, details = check_gate_condition(domain_results)
    assert passed is False


def test_verify_mechanism_activated():
    from evaluate import verify_mechanism_activated
    domain_results = {
        "cv": {"discriminability": {"p_value": 0.01, "cohens_d": 0.8, "auc": 0.85,
                                    "n_sat": 20, "n_healthy": 20},
               "baseline_auc": 0.6, "signal_auc": 0.85},
        "nlp": {"discriminability": {"p_value": 0.02, "cohens_d": 0.7, "auc": 0.80,
                                     "n_sat": 20, "n_healthy": 20},
                "baseline_auc": 0.58, "signal_auc": 0.80},
        "tabular": {"discriminability": {"p_value": 0.03, "cohens_d": 0.6, "auc": 0.75,
                                         "n_sat": 20, "n_healthy": 20},
                    "baseline_auc": 0.55, "signal_auc": 0.75},
    }
    activated, indicators = verify_mechanism_activated(domain_results)
    assert isinstance(activated, bool)
    assert isinstance(indicators, dict)
    for domain in ("cv", "nlp", "tabular"):
        assert domain in indicators


def test_save_results_creates_file(tmp_path):
    from evaluate import save_results
    results = {"gate_passed": True, "cv": {"p_value": 0.01}}
    out = str(tmp_path / "results.json")
    save_results(results, out)
    import os
    assert os.path.exists(out)
