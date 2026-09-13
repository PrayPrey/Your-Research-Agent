import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import json
from config import ExperimentConfig, TrainConfig, DFRConfig, AnalysisConfig, PathConfig
from results_exporter import ResultsExporter


@pytest.fixture
def cfg(tmp_path):
    return ExperimentConfig(
        train=TrainConfig(),
        dfr=DFRConfig(),
        analysis=AnalysisConfig(),
        paths=PathConfig(
            results_dir=str(tmp_path / "results"),
            figures_dir=str(tmp_path / "figures"),
            checkpoint_dir=str(tmp_path / "checkpoints"),
        ),
    )


@pytest.fixture
def sample_data():
    results_per_seed = {
        1: {1: {"erm_wga": 0.5, "dfr_wga": 0.6, "wga_improvement": 0.1, "feature_dim": 2048}},
    }
    aggregated = {
        1: {"mean_erm_wga": 0.5, "mean_dfr_wga": 0.6, "mean_wga_improvement": 0.1, "std_wga_improvement": 0.01}
    }
    corr = {"pearson_r": 0.85, "pearson_p_onetailed": 0.05, "epochs_past_tstar": [-1.0], "improvements": [0.1]}
    gate = {"gate_passed": True, "decision": "PASS", "threshold": 0.7, "note": "r>0.7", "pearson_r": 0.85}
    return results_per_seed, aggregated, corr, gate


def test_save_json_creates_file(cfg, sample_data):
    exporter = ResultsExporter(cfg)
    results_per_seed, aggregated, corr, gate = sample_data
    path = exporter.save_json(results_per_seed, aggregated, corr, gate, [])
    assert os.path.exists(path)


def test_save_json_valid_content(cfg, sample_data):
    exporter = ResultsExporter(cfg)
    results_per_seed, aggregated, corr, gate = sample_data
    path = exporter.save_json(results_per_seed, aggregated, corr, gate, [])
    with open(path) as f:
        data = json.load(f)
    assert "hypothesis_id" in data
    assert "results_per_seed" in data
    assert "gate" in data


def test_save_json_in_results_dir(cfg, sample_data):
    exporter = ResultsExporter(cfg)
    results_per_seed, aggregated, corr, gate = sample_data
    path = exporter.save_json(results_per_seed, aggregated, corr, gate, [])
    assert "results" in path


def test_print_summary_pass(cfg, sample_data, capsys):
    exporter = ResultsExporter(cfg)
    _, _, corr, gate = sample_data
    exporter.print_summary(corr, gate)
    captured = capsys.readouterr()
    assert "PASS" in captured.out
