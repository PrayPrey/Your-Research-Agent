"""Tests for task-007: run_experiment.py spec compliance."""
import subprocess
import sys
import os


CODE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_help_exits_cleanly():
    result = subprocess.run(
        [sys.executable, os.path.join(CODE_DIR, "run_experiment.py"), "--help"],
        capture_output=True, text=True, timeout=30
    )
    assert result.returncode == 0
    assert "usage" in result.stdout.lower() or "h-e1" in result.stdout.lower()


def test_config_dict_has_required_keys():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "run_experiment", os.path.join(CODE_DIR, "run_experiment.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    cfg = mod.CONFIG
    required_keys = ["seed", "n_bootstrap", "lookback_months", "output_dir",
                     "significance_level", "cohens_d_threshold"]
    for key in required_keys:
        assert key in cfg, f"Missing CONFIG key: {key}"
