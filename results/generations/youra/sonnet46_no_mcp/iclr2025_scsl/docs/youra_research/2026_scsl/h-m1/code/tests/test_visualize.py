import sys
import os
import tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from visualize import plot_mean_early_gdr_bar, plot_gdr_timeline


def test_plot_mean_early_gdr_bar_saves_png():
    analysis = {
        "mean_early_gdr_per_seed": {1: 1.5, 2: 1.3, 3: 1.2},
        "std_early_gdr": 0.15,
    }
    with tempfile.TemporaryDirectory() as tmpdir:
        path = plot_mean_early_gdr_bar(analysis, tmpdir)
        assert os.path.exists(path)
        assert path.endswith(".png")


def test_plot_gdr_timeline_saves_png():
    seed_results = {
        1: {"gdr_series": [1.8, 1.6, 1.4, 1.2, 1.1, 1.0, 0.98, 0.97, 0.96, 0.95, 0.94, 0.93, 0.92, 0.91, 0.90]},
        2: {"gdr_series": [1.7, 1.5, 1.3, 1.2, 1.05, 1.0, 0.99, 0.98, 0.97, 0.96, 0.95, 0.94, 0.93, 0.92, 0.91]},
    }
    delta_series = np.linspace(0.1, -0.05, 15)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = plot_gdr_timeline(seed_results, delta_series, tmpdir)
        assert os.path.exists(path)
        assert path.endswith(".png")


def test_figures_dir_created():
    analysis = {
        "mean_early_gdr_per_seed": {1: 1.5},
        "std_early_gdr": 0.1,
    }
    with tempfile.TemporaryDirectory() as tmpdir:
        new_subdir = os.path.join(tmpdir, "new_figures")
        path = plot_mean_early_gdr_bar(analysis, new_subdir)
        assert os.path.isdir(new_subdir)
        assert os.path.exists(path)
