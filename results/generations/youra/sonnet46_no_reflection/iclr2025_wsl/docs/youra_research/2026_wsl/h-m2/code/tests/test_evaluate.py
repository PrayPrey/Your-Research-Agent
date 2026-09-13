"""Tests for evaluate.py — task-007."""
import pytest
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from evaluate import (
    compute_cross_dataset_stability,
    check_gate,
    save_results_json,
)


def test_compute_cross_dataset_stability():
    result = compute_cross_dataset_stability(0.72, 0.68)
    assert "stability_gap" in result
    assert abs(result["stability_gap"] - 0.04) < 1e-6
    assert result["ratio_cifar10"] == 0.72
    assert result["ratio_svhn"] == 0.68


def test_compute_cross_dataset_stability_above_threshold():
    result = compute_cross_dataset_stability(0.80, 0.60)
    assert result["stability_gap"] == pytest.approx(0.20)


def test_check_gate_pass():
    results_c = {"ratio_mean": 0.70, "ratio_std": 0.05, "n_models": 250}
    results_s = {"ratio_mean": 0.68, "ratio_std": 0.04, "n_models": 220}
    gate = check_gate(results_c, results_s, threshold=0.60, stability_threshold=0.10)
    assert gate["primary_pass"] is True
    assert gate["n_models_pass"] is True
    assert gate["non_degenerate_pass"] is True
    assert gate["stability_pass"] is True
    assert gate["all_pass"] is True


def test_check_gate_fail_primary():
    results_c = {"ratio_mean": 0.50, "ratio_std": 0.05, "n_models": 250}
    results_s = {"ratio_mean": 0.48, "ratio_std": 0.04, "n_models": 220}
    gate = check_gate(results_c, results_s, threshold=0.60)
    assert gate["primary_pass"] is False
    assert gate["all_pass"] is False


def test_check_gate_fail_n_models():
    results_c = {"ratio_mean": 0.70, "ratio_std": 0.05, "n_models": 150}
    results_s = {"ratio_mean": 0.68, "ratio_std": 0.04, "n_models": 150}
    gate = check_gate(results_c, results_s, threshold=0.60)
    assert gate["n_models_pass"] is False
    assert gate["all_pass"] is False


def test_check_gate_stability_warning():
    results_c = {"ratio_mean": 0.75, "ratio_std": 0.05, "n_models": 250}
    results_s = {"ratio_mean": 0.60, "ratio_std": 0.04, "n_models": 220}
    gate = check_gate(results_c, results_s, stability_threshold=0.10)
    assert gate["stability_pass"] is False
    assert gate["all_pass"] is True  # stability is secondary, not blocking


def test_save_results_json(tmp_path):
    results = {"ratio_mean": 0.72, "n_models": 250, "gate_pass": True}
    out_file = str(tmp_path / "results.json")
    save_results_json(results, out_file)
    assert Path(out_file).exists()
    with open(out_file) as f:
        loaded = json.load(f)
    assert loaded["ratio_mean"] == 0.72


def test_save_results_json_with_list(tmp_path):
    results = {"ratios": [0.70, 0.72, 0.68], "nested": {"key": 42}}
    out_file = str(tmp_path / "out.json")
    save_results_json(results, out_file)
    with open(out_file) as f:
        loaded = json.load(f)
    assert loaded["ratios"] == [0.70, 0.72, 0.68]
