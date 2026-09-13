"""Spec compliance tests for visualize.py (H-E1)."""

import sys
import pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))


def test_plot_gate_metrics_creates_file(tmp_path):
    from visualize import plot_gate_metrics
    summary = {
        "mbpp+": {
            "type_error_fraction_mean": 0.20,
            "type_error_fraction_std": 0.03,
            "per_seed": {"42": {"fraction": 0.20}, "123": {"fraction": 0.18}, "456": {"fraction": 0.22}},
        },
        "humaneval+": {
            "type_error_fraction_mean": 0.15,
            "type_error_fraction_std": 0.02,
            "per_seed": {"42": {"fraction": 0.15}, "123": {"fraction": 0.14}, "456": {"fraction": 0.16}},
        },
    }
    plot_gate_metrics(summary, figures_dir=tmp_path)
    assert (tmp_path / "gate_metrics.png").exists()


def test_plot_error_type_dist_creates_file(tmp_path):
    from visualize import plot_error_type_dist
    results = [
        {"has_mypy_error": True, "error_count": 2, "error_categories": {"name-error": 1, "type-error": 1, "return-value": 0, "attribute-error": 0}},
        {"has_mypy_error": True, "error_count": 1, "error_categories": {"name-error": 0, "type-error": 0, "return-value": 1, "attribute-error": 0}},
    ]
    plot_error_type_dist(results, figures_dir=tmp_path)
    assert (tmp_path / "error_type_dist.png").exists()


def test_plot_error_count_hist_creates_file(tmp_path):
    from visualize import plot_error_count_hist
    results = [{"has_mypy_error": True, "error_count": i} for i in range(1, 10)]
    plot_error_count_hist(results, figures_dir=tmp_path)
    assert (tmp_path / "error_count_hist.png").exists()


def test_plot_seed_consistency_creates_file(tmp_path):
    from visualize import plot_seed_consistency
    summary = {
        "mbpp+": {
            "type_error_fraction_mean": 0.20,
            "type_error_fraction_std": 0.03,
            "per_seed": {"42": {"fraction": 0.20}, "123": {"fraction": 0.18}, "456": {"fraction": 0.22}},
        },
    }
    plot_seed_consistency(summary, figures_dir=tmp_path)
    assert (tmp_path / "seed_consistency.png").exists()


def test_generate_all_figures_creates_files(tmp_path):
    from visualize import generate_all_figures
    results = [
        {"has_mypy_error": True, "error_count": 2, "error_categories": {"name-error": 1, "type-error": 1, "return-value": 0, "attribute-error": 0}},
        {"has_mypy_error": False, "error_count": 0, "error_categories": {"name-error": 0, "type-error": 0, "return-value": 0, "attribute-error": 0}},
    ]
    summary = {
        "mbpp+": {
            "type_error_fraction_mean": 0.20,
            "type_error_fraction_std": 0.03,
            "per_seed": {"42": {"fraction": 0.20}, "123": {"fraction": 0.18}, "456": {"fraction": 0.22}},
        },
    }
    generate_all_figures(results, summary, figures_dir=tmp_path)
    assert (tmp_path / "gate_metrics.png").exists()
