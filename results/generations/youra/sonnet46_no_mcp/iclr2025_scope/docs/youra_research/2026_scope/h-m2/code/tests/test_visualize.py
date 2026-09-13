import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import matplotlib
matplotlib.use("Agg")

from evaluate import RunResult
from analyze import SpearmanAnalyzer
from visualize import (
    plot_gap_vs_budget, plot_spearman_bar, plot_gap_heatmap,
    plot_absolute_accuracy_curves, save_all_figures,
)
from config import LONGBENCH_TASKS, LONGBENCH_CATEGORIES


def make_results(model_name="gpt2"):
    categories = list(LONGBENCH_CATEGORIES.keys())
    results = []
    evict_scores = {0.25: 0.55, 0.50: 0.47, 0.75: 0.43}
    for adapter_type in ["sequential", "eviction-aware"]:
        for r in [0.25, 0.50, 0.75]:
            score = evict_scores[r] if adapter_type == "eviction-aware" else 0.4
            per_task = {t: score for t in LONGBENCH_TASKS}
            cat_scores = {c: score for c in categories}
            results.append(RunResult(model_name, adapter_type, r, per_task, cat_scores))
    return results


def test_plot_gap_vs_budget(tmp_path):
    results = make_results()
    analyzer = SpearmanAnalyzer()
    analysis = analyzer.run_full_analysis(results)
    out = str(tmp_path / "gap_vs_budget.png")
    plot_gap_vs_budget(analysis["gap_matrices"], out)
    assert os.path.exists(out)
    assert os.path.getsize(out) > 0


def test_plot_spearman_bar(tmp_path):
    results = make_results()
    analyzer = SpearmanAnalyzer()
    analysis = analyzer.run_full_analysis(results)
    out = str(tmp_path / "spearman_bar.png")
    plot_spearman_bar(analysis["spearman_results"], threshold=-0.8, output_path=out)
    assert os.path.exists(out)
    assert os.path.getsize(out) > 0


def test_plot_gap_heatmap(tmp_path):
    results = make_results()
    analyzer = SpearmanAnalyzer()
    analysis = analyzer.run_full_analysis(results)
    out = str(tmp_path / "gap_heatmap.png")
    plot_gap_heatmap(analysis["gap_matrices"], out)
    assert os.path.exists(out)
    assert os.path.getsize(out) > 0


def test_plot_absolute_accuracy_curves(tmp_path):
    results = make_results()
    out = str(tmp_path / "absolute_curves.png")
    plot_absolute_accuracy_curves(results, out)
    assert os.path.exists(out)
    assert os.path.getsize(out) > 0


def test_save_all_figures(tmp_path):
    results = make_results()
    analyzer = SpearmanAnalyzer()
    analysis = analyzer.run_full_analysis(results)
    figures_dir = str(tmp_path / "figures")
    save_all_figures(analysis, results, figures_dir)
    assert os.path.exists(os.path.join(figures_dir, "gap_vs_budget.png"))
    assert os.path.exists(os.path.join(figures_dir, "spearman_bar.png"))
    assert os.path.exists(os.path.join(figures_dir, "gap_heatmap.png"))
    assert os.path.exists(os.path.join(figures_dir, "absolute_curves.png"))
