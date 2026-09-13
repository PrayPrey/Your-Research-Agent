import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    H2ExperimentConfig, MypyRepairConfig, CScoreConfig, Z3DeltaConfig,
    H2OutputConfig, H2BaselinePoolConfig, H2IntegrationConfig, H2VisualizationConfig,
)


def test_h2_experiment_config_defaults():
    cfg = H2ExperimentConfig()
    assert cfg.hypothesis_id == "h-m2"
    assert cfg.n_problems == 164


def test_mypy_repair_config():
    cfg = MypyRepairConfig()
    assert cfg.max_rounds == 3
    assert cfg.repair_temperature == 0.2
    assert "--ignore-missing-imports" in cfg.mypy_flags
    assert "--no-error-summary" in cfg.mypy_flags


def test_c_score_config():
    cfg = CScoreConfig()
    assert cfg.n_bootstrap == 10000
    assert abs(cfg.alpha - 0.0167) < 1e-6
    assert cfg.seed == 42
    assert cfg.min_stratum_size == 10


def test_z3_delta_config():
    cfg = Z3DeltaConfig()
    assert cfg.z3_timeout_seconds == 60
    assert cfg.arith_density_threshold == 0.1


def test_integration_config_phases():
    cfg = H2IntegrationConfig()
    assert len(cfg.phases) == 8
    assert len(cfg.required_output_files) == 9
    assert cfg.dry_run_n_problems == 5


def test_visualization_config_colors():
    cfg = H2VisualizationConfig()
    assert "syncode" in cfg.colors
    assert "mypy" in cfg.colors
    assert len(cfg.figures) == 6
    assert cfg.dpi == 150
