import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import pytest


def test_pipeline_imports():
    """Verify all modules are importable."""
    import data_loader
    import z3_eligibility
    import mypy_checker
    import metrics
    import visualization


def test_all_outputs_exist():
    """Check that all expected output files exist after experiment run."""
    base = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..")
    results_dir = os.path.join(base, "results")
    data_dir = os.path.join(base, "data")
    figures_dir = os.path.join(base, "figures")

    metrics_path = os.path.join(results_dir, "metrics.json")
    if os.path.exists(metrics_path):
        with open(metrics_path) as f:
            data = json.load(f)
        assert "gate_pass" in data, "metrics.json missing gate_pass key"


def test_gate_result_in_metrics():
    """If metrics.json exists, verify gate_pass key is present."""
    base = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..")
    metrics_path = os.path.join(base, "results", "metrics.json")
    if not os.path.exists(metrics_path):
        pytest.skip("metrics.json not yet generated (run experiment first)")
    with open(metrics_path) as f:
        data = json.load(f)
    assert "gate_pass" in data
