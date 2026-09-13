"""Tests for task-005: AUROC evaluation."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import tempfile
import json
import pytest

from evaluate import (
    compute_auroc,
    bootstrap_auroc_ci,
    pairwise_auroc_differences,
    check_must_work_gate,
    save_results,
)
from config import get_config


def test_auroc_perfect():
    """All-correct → AUROC = 1.0."""
    labels = [0, 0, 1, 1]
    scores = [0.1, 0.2, 0.8, 0.9]
    assert compute_auroc(labels, scores) == 1.0


def test_auroc_random():
    """Random predictions → AUROC ≈ 0.5."""
    labels = [0, 1, 0, 1, 0, 1]
    scores = [0.5, 0.5, 0.5, 0.5, 0.5, 0.5]
    auroc = compute_auroc(labels, scores)
    assert 0.4 <= auroc <= 0.6


def test_bootstrap_ci_coverage():
    """CI should bracket the point estimate."""
    labels = [0] * 50 + [1] * 50
    scores = [float(i) / 100 for i in range(100)]
    lower, upper = bootstrap_auroc_ci(labels, scores, n_resamples=100, seed=42)
    point = compute_auroc(labels, scores)
    assert lower <= point <= upper
    assert upper > lower


def test_bootstrap_ci_seed_reproducibility():
    """Same seed → same CI."""
    labels = [0] * 50 + [1] * 50
    scores = [float(i) / 100 for i in range(100)]
    ci1 = bootstrap_auroc_ci(labels, scores, n_resamples=50, seed=7)
    ci2 = bootstrap_auroc_ci(labels, scores, n_resamples=50, seed=7)
    assert ci1 == ci2


def test_pairwise_differences():
    """Pairwise results have correct structure."""
    auroc_map = {"method_a": 0.8, "method_b": 0.6}
    ci_map = {"method_a": (0.75, 0.85), "method_b": (0.55, 0.65)}
    results = pairwise_auroc_differences(auroc_map, ci_map)
    assert len(results) == 1
    r = results[0]
    assert r["winner"] == "method_a"
    assert abs(r["delta_auroc"] - 0.2) < 1e-9
    assert r["ci_non_overlapping"] is True


def test_gate_pass():
    """Synthetic data with >0.05 gap → gate_passed=True."""
    cfg = get_config()
    pairwise = [{
        "method_a": "semantic_entropy",
        "method_b": "token_entropy_mean",
        "winner": "semantic_entropy",
        "loser": "token_entropy_mean",
        "auroc_winner": 0.78,
        "auroc_loser": 0.65,
        "delta_auroc": 0.13,
        "ci_lower_winner": 0.72,
        "ci_upper_winner": 0.84,
        "ci_lower_loser": 0.60,
        "ci_upper_loser": 0.70,
        "ci_non_overlapping": True,
    }]
    result = check_must_work_gate(pairwise, cfg)
    assert result["gate_passed"] is True


def test_gate_fail():
    """All methods same AUROC → gate_passed=False."""
    cfg = get_config()
    pairwise = [{
        "method_a": "semantic_entropy",
        "method_b": "token_entropy_mean",
        "winner": "semantic_entropy",
        "loser": "token_entropy_mean",
        "auroc_winner": 0.70,
        "auroc_loser": 0.68,
        "delta_auroc": 0.02,
        "ci_lower_winner": 0.65,
        "ci_upper_winner": 0.75,
        "ci_lower_loser": 0.63,
        "ci_upper_loser": 0.73,
        "ci_non_overlapping": False,
    }]
    result = check_must_work_gate(pairwise, cfg)
    assert result["gate_passed"] is False


def test_save_results():
    """Results files are created in correct location."""
    with tempfile.TemporaryDirectory() as d:
        auroc_map = {"semantic_entropy": 0.78, "token_entropy_mean": 0.65}
        ci_map = {"semantic_entropy": (0.72, 0.84), "token_entropy_mean": (0.60, 0.70)}
        pairwise = pairwise_auroc_differences(auroc_map, ci_map)
        cfg = get_config()
        gate = check_must_work_gate(pairwise, cfg)
        save_results(auroc_map, ci_map, pairwise, gate, d)
        assert (Path(d) / "h_e1_results.json").exists()
        assert (Path(d) / "h_e1_gate_check.json").exists()
