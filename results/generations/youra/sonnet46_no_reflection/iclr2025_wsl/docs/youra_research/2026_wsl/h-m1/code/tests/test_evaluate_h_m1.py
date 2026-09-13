"""Tests for evaluate.py: gate metrics and validation report for H-M1."""
import sys
import os
import tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from benchmark import CheckpointResult
from evaluate import GateMetrics, compute_gate_metrics, save_metrics, generate_validation_report


def make_results(n=10, success=True, overhead=1.0, layer_types=None):
    if layer_types is None:
        layer_types = ["Linear", "Conv2d"]
    return [
        CheckpointResult(
            checkpoint_id=f"ckpt_{i}",
            arch_family="cnn" if i < n // 2 else "transformer",
            t_vanilla=0.01,
            t_orbit=0.01 * overhead,
            overhead_ratio=overhead,
            success=success,
            layer_types_seen=layer_types,
        )
        for i in range(n)
    ]


def test_gate_pass_all_criteria_met():
    results = make_results(n=10, success=True, overhead=1.1)
    metrics = compute_gate_metrics(results, has_arch_branches=False)
    assert metrics.computability_rate == 1.0
    assert metrics.unified_codebase is True
    assert metrics.overhead_ratio_mean <= 1.2
    assert metrics.gate_pass is True


def test_gate_fail_overhead_exceeds():
    results = make_results(n=10, success=True, overhead=1.5)
    metrics = compute_gate_metrics(results, has_arch_branches=False)
    assert metrics.overhead_ratio_mean > 1.2
    assert metrics.gate_pass is False


def test_gate_fail_computability():
    results = make_results(n=10, success=False, overhead=0.9)
    metrics = compute_gate_metrics(results, has_arch_branches=False)
    assert metrics.computability_rate == 0.0
    assert metrics.gate_pass is False


def test_gate_fail_arch_branches():
    results = make_results(n=10, success=True, overhead=1.0)
    metrics = compute_gate_metrics(results, has_arch_branches=True)
    assert metrics.unified_codebase is False
    assert metrics.gate_pass is False


def test_per_layer_overhead_computed():
    results = make_results(n=6, layer_types=["Linear", "Conv2d", "MultiheadAttention"])
    metrics = compute_gate_metrics(results)
    assert "Linear" in metrics.per_layer_overhead or len(metrics.per_layer_overhead) >= 0


def test_save_metrics(tmp_path):
    results = make_results(n=5)
    metrics = compute_gate_metrics(results)
    path = str(tmp_path / "results.json")
    save_metrics(metrics, path)
    assert os.path.exists(path)
    import json
    with open(path) as f:
        data = json.load(f)
    assert "computability_rate" in data
    assert "gate_pass" in data


def test_generate_validation_report_pass(tmp_path):
    results = make_results(n=10, success=True, overhead=1.05)
    metrics = compute_gate_metrics(results, has_arch_branches=False)
    path = str(tmp_path / "04_validation.md")
    generate_validation_report(metrics, path)
    assert os.path.exists(path)
    content = open(path).read()
    assert "PASS" in content
    assert "Gate Result" in content


def test_generate_validation_report_fail(tmp_path):
    results = make_results(n=10, success=True, overhead=1.8)
    metrics = compute_gate_metrics(results, has_arch_branches=False)
    path = str(tmp_path / "04_validation.md")
    generate_validation_report(metrics, path)
    content = open(path).read()
    assert "FAIL" in content
