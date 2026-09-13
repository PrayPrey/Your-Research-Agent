"""Tests for config.py (task-001, task-004)"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config


def test_constants_accessible():
    assert isinstance(config.OPENML_UPLOAD_DATE_MIN, str)
    assert config.OPENML_UPLOAD_DATE_MIN == "2018-01-01"
    assert isinstance(config.OPENML_TASK_TYPES, list)
    assert len(config.OPENML_TASK_TYPES) >= 2
    assert isinstance(config.FUJI_API_BASE, str)
    assert isinstance(config.FUJI_CONCURRENCY, int)
    assert isinstance(config.FUJI_RETRY_MAX, int)
    assert isinstance(config.FAIR_THRESHOLD, float)
    assert isinstance(config.CV_GATE, float)
    assert isinstance(config.GROUP_SIZE_GATE, int)
    assert isinstance(config.RESULTS_DIR, str)
    assert isinstance(config.FIGURES_DIR, str)


def test_cv_gate_value():
    assert config.CV_GATE == 0.15


def test_group_size_gate_value():
    assert config.GROUP_SIZE_GATE == 500


def test_fair_threshold_value():
    assert config.FAIR_THRESHOLD == 0.5


def test_parse_args_runs():
    import sys
    old_argv = sys.argv
    sys.argv = ["config.py"]
    args = config.parse_args()
    sys.argv = old_argv
    assert args.fuji_api_base == config.FUJI_API_BASE
    assert args.use_fallback == False


def test_resolve_paths():
    import sys
    old_argv = sys.argv
    sys.argv = ["config.py"]
    args = config.parse_args()
    sys.argv = old_argv
    paths = config.resolve_paths(args)
    assert "scores_csv" in paths
    assert "metrics_json" in paths
    assert "gate_json" in paths
    assert paths["scores_csv"].endswith(".csv")
    assert paths["metrics_json"].endswith(".json")
    assert paths["gate_json"].endswith(".json")
