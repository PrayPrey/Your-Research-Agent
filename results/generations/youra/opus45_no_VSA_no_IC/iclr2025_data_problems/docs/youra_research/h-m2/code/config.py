"""Configuration for h-m2: Multi-seed dissociation experiment."""
import os
import sys
import importlib.util
from dataclasses import dataclass
from pathlib import Path

# Direct import from h-m1 config to avoid name collision
_hm1_config_path = str(Path(__file__).parent.parent.parent / "h-m1" / "code" / "config.py")
_spec = importlib.util.spec_from_file_location("h_m1_config", _hm1_config_path)
_h_m1_config = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_h_m1_config)

ExperimentConfig = _h_m1_config.ExperimentConfig
set_all_seeds = _h_m1_config.set_all_seeds
_setup_dirs = _h_m1_config.setup_dirs


@dataclass
class MultiSeedConfig(ExperimentConfig):
    """Extended config for multi-seed dissociation testing."""
    # ponytail: 3 seeds for CPU PoC; scale to 10 with GPU
    seeds: tuple = (42, 123, 456)

    # ponytail: minimal for CPU PoC; scale up for GPU
    epochs: int = 1
    probes_per_mode: int = 50

    ckpt_dir: str = "./h-m2/checkpoints"
    fig_dir: str = "./h-m2/figures"
    results_dir: str = "./h-m2/results"

    # Gate thresholds
    f_ratio_threshold: float = 4.0
    cohens_d_threshold: float = 0.5
    p_value_threshold: float = 0.05


def setup_dirs(cfg: MultiSeedConfig) -> None:
    """Setup directories including results_dir."""
    _setup_dirs(cfg)
    Path(cfg.results_dir).mkdir(parents=True, exist_ok=True)
