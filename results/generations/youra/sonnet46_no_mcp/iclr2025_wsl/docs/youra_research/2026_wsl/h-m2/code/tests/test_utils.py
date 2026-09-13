"""Tests for utils.py (task-003)."""
import sys
from pathlib import Path
import tempfile
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import ExperimentConfig
from utils import set_seed, setup_logging, save_results_yaml, ensure_dirs


def test_set_seed():
    set_seed(42)  # Should not raise


def test_setup_logging():
    logger = setup_logging()
    assert logger is not None


def test_ensure_dirs(tmp_path):
    cfg = ExperimentConfig(
        data_dir=tmp_path / "data",
        results_dir=tmp_path / "results",
        figures_dir=tmp_path / "figures",
    )
    ensure_dirs(cfg)
    assert cfg.results_dir.exists()
    assert cfg.figures_dir.exists()
    assert cfg.data_dir.exists()


def test_save_results_yaml(tmp_path):
    results = {"gate": {"passed": True}, "statistics": {"n_pairs": 500}}
    path = tmp_path / "results.yaml"
    save_results_yaml(results, path)
    assert path.exists()
    assert path.stat().st_size > 0
