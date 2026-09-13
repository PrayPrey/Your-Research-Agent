import os
import sys
import json
import math
import pytest
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from evaluate import RunResult
from analyze import SpearmanAnalyzer, GapMatrix, SpearmanResult, MonotonicityResult
from config import LONGBENCH_CATEGORIES, LONGBENCH_TASKS


def make_mock_results(model_name="gpt2", gap_trend="decreasing"):
    """Create mock RunResults with known Spearman pattern."""
    categories = list(LONGBENCH_CATEGORIES.keys())
    results = []

    # Sequential: constant scores
    for r in [0.25, 0.50, 0.75]:
        per_task = {t: 0.4 for t in LONGBENCH_TASKS}
        cat_scores = {cat: 0.4 for cat in categories}
        results.append(RunResult(
            model_name=model_name,
            adapter_type="sequential",
            budget_ratio=r,
            per_task_scores=per_task,
            category_scores=cat_scores,
        ))

    # Eviction-aware: gap increases as r decreases (gap25 > gap50 > gap75)
    # This means rho(r, gap) < 0 → should give negative Spearman
    if gap_trend == "decreasing":
        evict_scores = {0.25: 0.55, 0.50: 0.47, 0.75: 0.43}  # gap: 0.15, 0.07, 0.03
    else:
        evict_scores = {0.25: 0.43, 0.50: 0.47, 0.75: 0.55}  # gap increases with r

    for r in [0.25, 0.50, 0.75]:
        score = evict_scores[r]
        per_task = {t: score for t in LONGBENCH_TASKS}
        cat_scores = {cat: score for cat in categories}
        results.append(RunResult(
            model_name=model_name,
            adapter_type="eviction-aware",
            budget_ratio=r,
            per_task_scores=per_task,
            category_scores=cat_scores,
        ))

    return results


def test_compute_gap_matrix_structure():
    results = make_mock_results()
    analyzer = SpearmanAnalyzer()
    gap_matrices = analyzer.compute_gap_matrix(results)

    assert "gpt2" in gap_matrices
    gm = gap_matrices["gpt2"]
    assert isinstance(gm, GapMatrix)
    assert len(gm.mean_gaps) == 3
    assert set(gm.mean_gaps.keys()) == {0.25, 0.50, 0.75}


def test_compute_gap_matrix_values():
    results = make_mock_results()
    analyzer = SpearmanAnalyzer()
    gm = analyzer.compute_gap_matrix(results)["gpt2"]

    # gap(0.25) = 0.55 - 0.4 = 0.15, gap(0.50) = 0.07, gap(0.75) = 0.03
    assert abs(gm.mean_gaps[0.25] - 0.15) < 1e-4
    assert abs(gm.mean_gaps[0.50] - 0.07) < 1e-4
    assert abs(gm.mean_gaps[0.75] - 0.03) < 1e-4


def test_spearman_gate_passed_when_rho_below_threshold():
    """gate_passed == True iff rho < -0.8."""
    results = make_mock_results(gap_trend="decreasing")
    analyzer = SpearmanAnalyzer()
    gm = analyzer.compute_gap_matrix(results)["gpt2"]
    sr = analyzer.compute_spearman(gm)

    assert isinstance(sr, SpearmanResult)
    assert sr.rho < -0.8, f"Expected rho < -0.8, got {sr.rho}"
    assert sr.gate_passed is True


def test_spearman_gate_failed_when_rho_above_threshold():
    """gate_passed == False when rho >= -0.8."""
    results = make_mock_results(gap_trend="increasing")
    analyzer = SpearmanAnalyzer()
    gm = analyzer.compute_gap_matrix(results)["gpt2"]
    sr = analyzer.compute_spearman(gm)

    assert sr.gate_passed is False


def test_monotonicity_result():
    results = make_mock_results(gap_trend="decreasing")
    analyzer = SpearmanAnalyzer()
    gm = analyzer.compute_gap_matrix(results)["gpt2"]
    mr = analyzer.check_monotonicity(gm)

    assert isinstance(mr, MonotonicityResult)
    assert 0.0 <= mr.fraction_monotone <= 1.0
    # All categories should be monotone (gap25 > gap50 > gap75)
    assert mr.fraction_monotone == 1.0


def test_run_full_analysis_structure():
    results = make_mock_results()
    analyzer = SpearmanAnalyzer()
    analysis = analyzer.run_full_analysis(results)

    assert "gap_matrices" in analysis
    assert "spearman_results" in analysis
    assert "monotonicity" in analysis
    assert "gate_passed" in analysis
    assert isinstance(analysis["gate_passed"], bool)


def test_save_summary_json(tmp_path):
    results = make_mock_results()
    analyzer = SpearmanAnalyzer()
    analysis = analyzer.run_full_analysis(results)

    output_path = str(tmp_path / "summary.json")
    analyzer.save_summary(analysis, output_path)

    assert os.path.exists(output_path)
    with open(output_path) as f:
        data = json.load(f)
    assert "gate_passed" in data
    assert "spearman_results" in data
    assert isinstance(data["gate_passed"], bool)
