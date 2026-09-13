"""Tests for visualization module."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'code'))

import tempfile
from visualize import ExperimentVisualizer


def test_visualizer_initialization():
    """Test ExperimentVisualizer can be initialized."""
    with tempfile.TemporaryDirectory() as tmpdir:
        visualizer = ExperimentVisualizer(results_dir=tmpdir)
        assert visualizer.results_dir == tmpdir
        assert os.path.exists(tmpdir)


def test_gate_metrics_plot():
    """Test gate metrics plot generation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        visualizer = ExperimentVisualizer(results_dir=tmpdir)

        metrics = {
            'baseline_mean_sr': 100.0,
            'proposed_mean_sr': 75.0,
            'baseline_perplexity': 50.0,
            'proposed_perplexity': 50.5,
            'proposed_layer_variance': 1.5,
            'proposed_measurement_cv': 0.12
        }

        targets = {
            'target_sr_reduction': 0.20,
            'target_ppl_deviation': 0.01,
            'target_layer_variance_ratio': 2.0,
            'target_measurement_cv': 0.15
        }

        output_path = os.path.join(tmpdir, 'test_gate.png')
        visualizer.plot_gate_metrics(metrics, targets, output_path=output_path)
        assert os.path.exists(output_path)


def test_stable_rank_distribution_plot():
    """Test stable rank distribution plot."""
    with tempfile.TemporaryDirectory() as tmpdir:
        visualizer = ExperimentVisualizer(results_dir=tmpdir)

        stable_ranks = {f'layer_{i}': 10.0 + i for i in range(12)}
        output_path = os.path.join(tmpdir, 'test_dist.png')
        visualizer.plot_stable_rank_distribution(stable_ranks, output_path=output_path)
        assert os.path.exists(output_path)
