import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import pytest

from analysis import (
    compute_aggregation_rate,
    compute_collapse_rate,
    compute_distribution_stats,
    bootstrap_aggregation_ci,
    compute_pointbiserial_correlation,
    evaluate_gate,
    validate_results_schema,
    RESULTS_SCHEMA,
)
from config import ExperimentConfig


def test_compute_aggregation_rate_pass(cluster_counts_pass):
    rate = compute_aggregation_rate(cluster_counts_pass, n_samples=5)
    assert rate >= 0.50


def test_compute_aggregation_rate_pivot(cluster_counts_pivot):
    rate = compute_aggregation_rate(cluster_counts_pivot, n_samples=5)
    assert rate < 0.30


def test_compute_aggregation_rate_all_five():
    counts = np.full(100, 5, dtype=int)
    assert compute_aggregation_rate(counts, n_samples=5) == 0.0


def test_compute_aggregation_rate_all_one():
    counts = np.ones(100, dtype=int)
    assert compute_aggregation_rate(counts, n_samples=5) == 1.0


def test_compute_collapse_rate(cluster_counts_pivot):
    rate = compute_collapse_rate(cluster_counts_pivot)
    assert 0.0 <= rate <= 1.0


def test_compute_collapse_rate_all_one():
    counts = np.ones(100, dtype=int)
    assert compute_collapse_rate(counts) == 1.0


def test_compute_distribution_stats(cluster_counts_pass):
    stats = compute_distribution_stats(cluster_counts_pass)
    assert "mean_cluster_count" in stats
    assert "std_cluster_count" in stats
    assert "median_cluster_count" in stats
    assert "histogram" in stats
    hist = stats["histogram"]
    assert set(hist.keys()) == {"1", "2", "3", "4", "5"}
    assert sum(hist.values()) == 2000


def test_bootstrap_ci_shape(cluster_counts_pass):
    result = bootstrap_aggregation_ci(cluster_counts_pass, n_resamples=200, seed=42)
    assert {"aggregation_rate", "ci_lower", "ci_upper", "gate_pass"} <= result.keys()


def test_bootstrap_ci_deterministic(cluster_counts_pass):
    r1 = bootstrap_aggregation_ci(cluster_counts_pass, n_resamples=200, seed=42)
    r2 = bootstrap_aggregation_ci(cluster_counts_pass, n_resamples=200, seed=42)
    assert r1["ci_lower"] == r2["ci_lower"]
    assert r1["ci_upper"] == r2["ci_upper"]


def test_bootstrap_ci_gate_pass_false_low_rate(cluster_counts_pivot):
    result = bootstrap_aggregation_ci(cluster_counts_pivot, n_resamples=200, seed=42)
    assert result["gate_pass"] is False


def test_evaluate_gate_pass(cluster_counts_pass):
    cfg = ExperimentConfig()
    result = bootstrap_aggregation_ci(cluster_counts_pass, n_resamples=200, seed=42)
    assert evaluate_gate(result, cfg) == "PASS"


def test_evaluate_gate_pivot(cluster_counts_pivot):
    cfg = ExperimentConfig()
    result = bootstrap_aggregation_ci(cluster_counts_pivot, n_resamples=200, seed=42)
    assert evaluate_gate(result, cfg) == "PIVOT"


def test_evaluate_gate_partial(cluster_counts_partial):
    cfg = ExperimentConfig()
    result = bootstrap_aggregation_ci(cluster_counts_partial, n_resamples=200, seed=42)
    gate = evaluate_gate(result, cfg)
    assert gate in ("PARTIAL", "PIVOT")  # partial fixture ~0.38


def test_evaluate_gate_explicit_pass():
    cfg = ExperimentConfig()
    result = {"aggregation_rate": 0.55, "ci_lower": 0.45, "ci_upper": 0.65, "gate_pass": True}
    assert evaluate_gate(result, cfg) == "PASS"


def test_evaluate_gate_explicit_partial():
    cfg = ExperimentConfig()
    result = {"aggregation_rate": 0.40, "ci_lower": 0.25, "ci_upper": 0.55, "gate_pass": False}
    assert evaluate_gate(result, cfg) == "PARTIAL"


def test_evaluate_gate_explicit_pivot():
    cfg = ExperimentConfig()
    result = {"aggregation_rate": 0.13, "ci_lower": 0.10, "ci_upper": 0.16, "gate_pass": False}
    assert evaluate_gate(result, cfg) == "PIVOT"


def test_pointbiserial_correlation(mock_labels, cluster_counts_pass):
    result = compute_pointbiserial_correlation(mock_labels, cluster_counts_pass)
    assert "r_pb" in result
    assert "p_value" in result
    assert "meaningful" in result
    assert -1.0 <= result["r_pb"] <= 1.0
    assert 0.0 <= result["p_value"] <= 1.0


def test_validate_results_schema_pass():
    results = {k: None for k in RESULTS_SCHEMA["required_keys"]}
    validate_results_schema(results)  # should not raise


def test_validate_results_schema_missing_key():
    results = {k: None for k in RESULTS_SCHEMA["required_keys"]}
    del results["gate_result"]
    with pytest.raises(KeyError):
        validate_results_schema(results)
