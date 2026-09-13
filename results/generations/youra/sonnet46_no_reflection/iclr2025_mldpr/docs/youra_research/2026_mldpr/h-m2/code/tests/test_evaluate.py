"""Tests for A-7: evaluate.py spec compliance (H-M1 API)."""
import pytest
import numpy as np
import pandas as pd


def _make_panel_df(n=50):
    rng = np.random.default_rng(42)
    return pd.DataFrame({
        "benchmark_id": [f"bench_{i % 10}" for i in range(n)],
        "quarter": [f"202{i//10}Q{(i%4)+1}" for i in range(n)],
        "cumulative_count": rng.integers(10, 500, n).astype(float),
        "compression_event": rng.integers(0, 2, n).astype(float),
    })


def test_verify_mechanism_activated_returns_tuple():
    from evaluate import verify_mechanism_activated
    panel_df = _make_panel_df(n=300)
    granger_results = {f"bench_{i}": {1: 0.01, 2: 0.02, 3: 0.05, 4: 0.1} for i in range(35)}
    spearman_result = {"rho": 0.5, "p_value": 0.01, "n_obs": 200}
    activated, indicators = verify_mechanism_activated(panel_df, granger_results, spearman_result)
    assert isinstance(activated, bool)
    assert isinstance(indicators, dict)
    for key in ("panel_constructed", "sufficient_benchmarks", "spearman_computed",
                "granger_computed", "spearman_significant", "granger_significant_lag2"):
        assert key in indicators, f"Missing indicator key: {key}"


def test_verify_mechanism_activated_triggers():
    from evaluate import verify_mechanism_activated
    panel_df = _make_panel_df(n=300)
    granger_results = {f"bench_{i}": {1: 0.01, 2: 0.01} for i in range(35)}
    spearman_result = {"rho": 0.6, "p_value": 0.001, "n_obs": 200}
    activated, indicators = verify_mechanism_activated(panel_df, granger_results, spearman_result)
    assert indicators["spearman_significant"] is True
    assert indicators["granger_significant_lag2"] is True


def test_check_gate_condition_pass():
    from evaluate import check_gate_condition
    spearman_result = {"rho": 0.55, "p_value": 0.01, "n_obs": 200}
    granger_agg = {"min_p_lag2": 0.001, "n_significant_lag2": 20, "pct_significant_lag2": 0.5}
    passed, details = check_gate_condition(spearman_result, granger_agg)
    assert passed is True
    assert "gate_passed" in details


def test_check_gate_condition_fail():
    from evaluate import check_gate_condition
    spearman_result = {"rho": 0.1, "p_value": 0.5, "n_obs": 50}
    granger_agg = {"min_p_lag2": 0.5, "n_significant_lag2": 0, "pct_significant_lag2": 0.0}
    passed, details = check_gate_condition(spearman_result, granger_agg)
    assert passed is False


def test_save_results_creates_file(tmp_path):
    from evaluate import save_results
    results = {"gate_passed": True, "granger_min_p": 0.001}
    out = str(tmp_path / "results.json")
    save_results(results, out)
    import os
    assert os.path.exists(out)
