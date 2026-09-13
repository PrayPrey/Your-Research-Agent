"""Tests for metrics module."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from metrics import compute_per_task_gap, bootstrap_ci, aggregate_metrics


def test_compute_per_task_gap_all_violated():
    results = [
        {"task_id": "A", "model": "m1", "violated": True, "n_total": 2, "error": None},
        {"task_id": "A", "model": "m1", "violated": True, "n_total": 2, "error": None},
        {"task_id": "B", "model": "m1", "violated": False, "n_total": 2, "error": None},
    ]
    gap = compute_per_task_gap(results)
    assert gap["A"] == 1.0
    assert gap["B"] == 0.0


def test_compute_per_task_gap_mixed():
    results = [
        {"task_id": "A", "model": "m1", "violated": True, "n_total": 1, "error": None},
        {"task_id": "A", "model": "m2", "violated": False, "n_total": 1, "error": None},
    ]
    gap = compute_per_task_gap(results)
    assert gap["A"] == 0.5


def test_compute_per_task_gap_skips_exec_errors():
    results = [
        {"task_id": "A", "model": "m1", "violated": False, "n_total": 0, "error": "exec error"},
        {"task_id": "A", "model": "m2", "violated": True, "n_total": 2, "error": None},
    ]
    gap = compute_per_task_gap(results)
    # Only the non-error result counted
    assert gap["A"] == 1.0


def test_bootstrap_ci_high_gaps():
    gaps = [0.8] * 100
    lo, hi = bootstrap_ci(gaps, n_bootstrap=1000, seed=42)
    assert lo > 0.01
    assert lo <= hi
    assert abs(lo - 0.8) < 0.05


def test_bootstrap_ci_empty():
    lo, hi = bootstrap_ci([])
    assert lo == 0.0
    assert hi == 0.0


def test_aggregate_metrics_gate_pass():
    # All tasks have 100% gap → CI_lower should be >> 0.01
    results = []
    for i in range(50):
        results.append({
            "task_id": f"T{i}", "model": "m1",
            "violated": True, "n_total": 5, "error": None
        })
    metrics = aggregate_metrics(results, z3_tractable_ids=set(), n_bootstrap=1000)
    assert metrics["mean_gap"] == 1.0
    assert metrics["gate_passed"] is True
    assert metrics["n_tasks"] == 50


def test_aggregate_metrics_gate_fail():
    results = [
        {"task_id": "A", "model": "m1", "violated": False, "n_total": 5, "error": None},
    ]
    metrics = aggregate_metrics(results, z3_tractable_ids=set(), n_bootstrap=100)
    assert metrics["mean_gap"] == 0.0
    assert metrics["gate_passed"] is False
