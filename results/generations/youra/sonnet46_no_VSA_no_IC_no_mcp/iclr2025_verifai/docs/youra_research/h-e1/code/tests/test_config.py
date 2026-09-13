"""Spec compliance tests for config.py (H-E1)."""

import sys
import pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))


def test_experiment_config_defaults():
    from config import ExperimentConfig
    cfg = ExperimentConfig()
    assert cfg.model == "gpt-4o-mini"
    assert cfg.temperature == 0.8
    assert cfg.max_tokens == 1024
    assert cfg.seeds == [42, 123, 456]
    assert "mbpp+" in cfg.benchmarks
    assert "humaneval+" in cfg.benchmarks
    assert cfg.gate_pass == 0.10
    assert cfg.gate_borderline == 0.05


def test_experiment_config_from_yaml(tmp_path):
    from config import ExperimentConfig
    yaml_content = """
model: "gpt-4o-mini"
temperature: 0.8
max_tokens: 1024
seeds: [42, 123, 456]
benchmarks: ["mbpp+", "humaneval+"]
mypy_timeout: 30
mypy_flags:
  - "--ignore-missing-imports"
  - "--no-strict-optional"
results_dir: "docs/youra_research/h-e1/results"
figures_dir: "docs/youra_research/h-e1/figures"
gate_pass: 0.10
gate_borderline: 0.05
"""
    cfg_file = tmp_path / "config.yaml"
    cfg_file.write_text(yaml_content)
    cfg = ExperimentConfig.from_yaml(str(cfg_file))
    assert cfg.model == "gpt-4o-mini"
    assert cfg.seeds == [42, 123, 456]


def test_figure_config_defaults():
    from visualize import FigureConfig, FIG
    cfg = FigureConfig()
    assert cfg.gate_threshold == 0.10
    assert cfg.gate_metrics == "gate_metrics.png"
    assert cfg.error_type_dist == "error_type_dist.png"
    assert cfg.error_count_hist == "error_count_hist.png"
    assert cfg.seed_consistency == "seed_consistency.png"
    # Singleton exists
    assert FIG is not None
    assert isinstance(FIG, FigureConfig)
