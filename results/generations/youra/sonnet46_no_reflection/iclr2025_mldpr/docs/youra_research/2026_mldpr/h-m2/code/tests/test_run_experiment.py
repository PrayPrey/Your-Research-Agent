"""Tests for A-9: run_experiment.py spec compliance (H-M1 API)."""
import importlib.util
import os
import sys

CODE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_config_dict_has_required_keys():
    spec = importlib.util.spec_from_file_location(
        "run_experiment", os.path.join(CODE_DIR, "run_experiment.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    cfg = mod.CONFIG
    required_keys = ["seed", "min_submissions", "min_quarters", "compression_threshold",
                     "granger_max_lag", "significance_level", "output_dir"]
    for key in required_keys:
        assert key in cfg, f"Missing CONFIG key: {key}"


def test_parse_args_returns_dict():
    spec = importlib.util.spec_from_file_location(
        "run_experiment", os.path.join(CODE_DIR, "run_experiment.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    result = mod.parse_args(mod.CONFIG, args=[])
    assert isinstance(result, dict)
    assert "seed" in result
    assert "output_dir" in result
