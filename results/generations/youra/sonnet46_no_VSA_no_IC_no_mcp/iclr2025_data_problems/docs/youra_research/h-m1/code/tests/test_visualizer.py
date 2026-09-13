"""Tests for visualizer.py — A-8."""
import sys
import tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from visualizer import sig_stars


def test_sig_stars_levels():
    assert sig_stars(0.0001) == "***"
    assert sig_stars(0.005) == "**"
    assert sig_stars(0.03) == "*"
    assert sig_stars(0.1) == "ns"
    assert sig_stars(None) == "ns"


def test_plot_overlap_bar_creates_file():
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "bar.png"
        overlap_scores = {
            "removed": {"mmlu": [0.1, 0.2, 0.15], "hellaswag": [0.05, 0.06, 0.04]},
            "retained": {"mmlu": [0.01, 0.02, 0.015], "hellaswag": [0.01, 0.02, 0.015]},
        }
        stats = {
            "per_benchmark": {
                "mmlu": {"p_corrected": 0.001, "significant": True},
                "hellaswag": {"p_corrected": 0.1, "significant": False},
            }
        }
        from visualizer import plot_overlap_bar
        plot_overlap_bar(overlap_scores, stats, out=out)
        assert out.exists()
        assert out.stat().st_size > 0


def test_plot_violin_creates_file():
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "violin.png"
        overlap_scores = {
            "removed": {"mmlu": [0.1] * 20, "hellaswag": [0.05] * 20},
            "retained": {"mmlu": [0.01] * 20, "hellaswag": [0.01] * 20},
        }
        from visualizer import plot_violin
        plot_violin(overlap_scores, out=out)
        assert out.exists()


def test_plot_rank_correlation_creates_file():
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "rank.png"
        stats = {
            "per_benchmark": {
                "mmlu": {"mean_removed": 0.1, "mean_retained": 0.01, "p_corrected": 0.001, "significant": True},
                "arc_challenge": {"mean_removed": 0.07, "mean_retained": 0.01, "p_corrected": 0.01, "significant": True},
                "hellaswag": {"mean_removed": 0.04, "mean_retained": 0.01, "p_corrected": 0.05, "significant": False},
                "winogrande": {"mean_removed": 0.01, "mean_retained": 0.01, "p_corrected": 0.5, "significant": False},
            },
            "spearman": {"correlation": 0.8, "p_value": 0.2},
        }
        from visualizer import plot_rank_correlation
        plot_rank_correlation(stats, out=out)
        assert out.exists()
