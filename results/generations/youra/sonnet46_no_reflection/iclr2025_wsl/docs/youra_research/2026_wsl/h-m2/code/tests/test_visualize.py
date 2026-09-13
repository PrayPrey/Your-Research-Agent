"""Tests for visualize.py — task-008."""
import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from visualize import (
    plot_gate_bar_chart,
    plot_ratio_histogram,
    plot_ratio_vs_epoch,
    plot_layer_breakdown,
    plot_ratio_vs_accuracy,
    save_all_figures,
)


def make_results():
    return {
        "cifar10": {
            "ratio_mean": 0.72,
            "ratio_std": 0.05,
            "n_models": 250,
            "ratios": [0.65, 0.70, 0.72, 0.75, 0.68],
            "epoch_ratios": [[0.5, 0.6, 0.7, 0.72], [0.4, 0.55, 0.65, 0.70]],
            "layer_stats": {
                "Conv2d": {"var_perm": 100.0, "var_gl": 40.0, "ratio": 0.71},
                "Linear": {"var_perm": 80.0, "var_gl": 30.0, "ratio": 0.73},
            },
            "var_perm_mean": 500.0,
            "var_gl_mean": 200.0,
        },
        "svhn": {
            "ratio_mean": 0.69,
            "ratio_std": 0.04,
            "n_models": 230,
            "ratios": [0.65, 0.68, 0.70],
            "epoch_ratios": [[0.5, 0.6, 0.68]],
            "layer_stats": {},
            "var_perm_mean": 480.0,
            "var_gl_mean": 210.0,
        },
        "gate_threshold": 0.60,
        "accuracies_cifar10": [0.85, 0.88, 0.87, 0.90, 0.86],
    }


def test_plot_gate_bar_chart_creates_file(tmp_path):
    results = make_results()
    out = tmp_path / "gate_bar.png"
    plot_gate_bar_chart(results["cifar10"], results["svhn"], 0.60, out)
    assert out.exists()
    assert out.stat().st_size > 0


def test_plot_ratio_histogram_creates_file(tmp_path):
    results = make_results()
    out = tmp_path / "histogram.png"
    plot_ratio_histogram(
        results["cifar10"]["ratios"],
        results["svhn"]["ratios"],
        out
    )
    assert out.exists()


def test_plot_ratio_vs_epoch_creates_file(tmp_path):
    results = make_results()
    out = tmp_path / "epoch.png"
    plot_ratio_vs_epoch(results["cifar10"]["epoch_ratios"], out)
    assert out.exists()


def test_plot_ratio_vs_epoch_empty_data(tmp_path):
    out = tmp_path / "epoch_empty.png"
    plot_ratio_vs_epoch([], out)
    assert out.exists()


def test_plot_layer_breakdown_creates_file(tmp_path):
    results = make_results()
    out = tmp_path / "layer.png"
    plot_layer_breakdown(results["cifar10"]["layer_stats"], out)
    assert out.exists()


def test_plot_ratio_vs_accuracy_creates_file(tmp_path):
    results = make_results()
    out = tmp_path / "scatter.png"
    plot_ratio_vs_accuracy(
        results["cifar10"]["ratios"],
        results["accuracies_cifar10"],
        out
    )
    assert out.exists()


def test_save_all_figures_creates_all(tmp_path):
    results = make_results()
    save_all_figures(results, tmp_path)
    expected = [
        "gate_bar_chart.png",
        "ratio_histogram.png",
        "ratio_vs_epoch.png",
        "layer_breakdown.png",
        "ratio_vs_accuracy.png",
    ]
    for fname in expected:
        assert (tmp_path / fname).exists(), f"Missing: {fname}"
