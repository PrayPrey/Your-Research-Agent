"""Tests for task-006: visualization."""
import sys
import tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for tests
import matplotlib.pyplot as plt

from visualize import plot_auroc_bar_chart, plot_roc_curves_overlay


AUROC_MAP = {
    "semantic_entropy": 0.78,
    "token_entropy_mean": 0.65,
    "selfcheckgpt_bertscore_n5": 0.72,
}
CI_MAP = {
    "semantic_entropy": (0.72, 0.84),
    "token_entropy_mean": (0.60, 0.70),
    "selfcheckgpt_bertscore_n5": (0.66, 0.78),
}
LABELS = [0] * 50 + [1] * 50
SCORES_MAP = {
    "semantic_entropy": [float(i) / 100 for i in range(100)],
    "token_entropy_mean": [float(i) / 130 for i in range(100)],
    "selfcheckgpt_bertscore_n5": [float(i) / 115 for i in range(100)],
}


def test_bar_chart_created():
    with tempfile.TemporaryDirectory() as d:
        save_path = str(Path(d) / "auroc_bar_chart.png")
        plot_auroc_bar_chart(AUROC_MAP, CI_MAP, save_path)
        assert Path(save_path).exists()
        assert Path(save_path).stat().st_size > 0


def test_roc_curves_created():
    with tempfile.TemporaryDirectory() as d:
        save_path = str(Path(d) / "roc_curves_overlay.png")
        plot_roc_curves_overlay(LABELS, SCORES_MAP, AUROC_MAP, save_path)
        assert Path(save_path).exists()
        assert Path(save_path).stat().st_size > 0


def test_figure_readable():
    """Matplotlib can re-read the saved PNG."""
    with tempfile.TemporaryDirectory() as d:
        save_path = str(Path(d) / "test.png")
        plot_auroc_bar_chart(AUROC_MAP, CI_MAP, save_path)
        img = plt.imread(save_path)
        assert img is not None
        assert len(img.shape) in (2, 3)
