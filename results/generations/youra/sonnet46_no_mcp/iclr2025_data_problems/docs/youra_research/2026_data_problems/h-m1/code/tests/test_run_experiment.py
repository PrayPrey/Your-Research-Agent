import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import tempfile
import pandas as pd
from unittest.mock import patch, MagicMock
from config import Config, load_config


def _make_mock_labels(n_subtasks=59, n_items=50):
    """Create mock labels with variance for testing."""
    labels = {}
    for i in range(n_subtasks):
        rate = i / n_subtasks
        c = int(rate * n_items)
        labels[f"subtask_{i}"] = [1] * c + [0] * (n_items - c)
    return labels


def test_main_runs_end_to_end_with_mocked_pile_query():
    with tempfile.TemporaryDirectory() as tmpdir:
        cfg = Config(results_dir=os.path.join(tmpdir, "results"),
                     figures_dir=os.path.join(tmpdir, "figures"))

        mock_labels = _make_mock_labels()

        with patch("run_experiment.DataLoader") as MockLoader, \
             patch("run_experiment.PileQuery") as MockQuery, \
             patch("run_experiment.Visualizer"):

            mock_loader_inst = MockLoader.return_value
            mock_loader_inst.load_all.return_value = {
                k: [f"text {j}" for j in range(50)] for k in mock_labels
            }

            mock_query_inst = MockQuery.return_value
            mock_query_inst.mode = "fallback_minhash"
            mock_query_inst.query_all.return_value = mock_labels

            from run_experiment import run_primary
            result = run_primary(cfg)

        assert "rates_df" in result
        assert "stats" in result
        assert "labels" in result
        assert result["stats"]["p_value"] < 0.05


def test_run_sensitivity_produces_59_key_rates_df():
    with tempfile.TemporaryDirectory() as tmpdir:
        cfg = Config(results_dir=os.path.join(tmpdir, "results"),
                     figures_dir=os.path.join(tmpdir, "figures"))

        mock_labels = _make_mock_labels(59, 50)
        primary_rates = pd.DataFrame([
            {"subtask": k, "n_items": 50,
             "n_contaminated": sum(v), "rate": sum(v) / 50}
            for k, v in mock_labels.items()
        ])

        with patch("run_experiment.DataLoader") as MockLoader, \
             patch("run_experiment.PileQuery") as MockQuery, \
             patch("run_experiment.Visualizer"):

            mock_loader_inst = MockLoader.return_value
            mock_loader_inst.load_all.return_value = {
                k: [f"text {j}" for j in range(50)] for k in mock_labels
            }
            mock_query_inst = MockQuery.return_value
            mock_query_inst.mode = "fallback_minhash"
            mock_query_inst.query_all.return_value = mock_labels

            from run_experiment import run_sensitivity
            result = run_sensitivity(cfg, primary_rates)

        assert "sensitivity_rates_df" in result
        assert len(result["sensitivity_rates_df"]) == 59
        assert "rho" in result


def test_gate_assertion_called_after_run_primary():
    from stats_analyzer import StatsAnalyzer as RealAnalyzer

    with tempfile.TemporaryDirectory() as tmpdir:
        cfg = Config(results_dir=os.path.join(tmpdir, "results"),
                     figures_dir=os.path.join(tmpdir, "figures"),
                     gate_p_threshold=0.05)

        mock_labels = _make_mock_labels()
        mock_analyzer_inst = MagicMock(spec=RealAnalyzer)
        mock_analyzer_inst.compute_rates.return_value = pd.DataFrame([
            {"subtask": k, "n_items": 50, "n_contaminated": 10, "rate": 0.2}
            for k in mock_labels
        ])
        mock_analyzer_inst.kruskal_wallis.return_value = {
            "kruskal_stat": 100.0, "p_value": 0.0001,
            "gate_pass": True, "max_pair_diff": 0.5
        }

        with patch("run_experiment.DataLoader") as MockLoader, \
             patch("run_experiment.PileQuery") as MockQuery, \
             patch("run_experiment.Visualizer"), \
             patch("run_experiment.StatsAnalyzer", return_value=mock_analyzer_inst):

            mock_loader_inst = MockLoader.return_value
            mock_loader_inst.load_all.return_value = {
                k: ["text"] * 50 for k in mock_labels
            }
            mock_query_inst = MockQuery.return_value
            mock_query_inst.mode = "fallback_minhash"
            mock_query_inst.query_all.return_value = mock_labels

            from run_experiment import run_primary
            run_primary(cfg)

        mock_analyzer_inst.assert_gate.assert_called_once_with(0.0001)
