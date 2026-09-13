"""ExperimentConfig for H-M2: Permutation Orbit Variance Dominance."""
from dataclasses import dataclass
from pathlib import Path
import yaml
import os


H_M1_CODE_PATH: str = "docs/youra_research/20260521_wsl/h-m1/code"


@dataclass
class ExperimentConfig:
    # Paths
    data_dir_cifar10: str = "data/cnn_zoo_cifar10"
    data_dir_svhn: str = "data/cnn_zoo_svhn"
    figures_dir: str = "docs/youra_research/20260521_wsl/h-m2/figures"
    results_dir: str = "docs/youra_research/20260521_wsl/h-m2/results"
    h_m1_code_path: str = H_M1_CODE_PATH

    # Data / trajectory parameters
    min_models: int = 200
    min_checkpoints: int = 10
    max_checkpoints: int = 50
    n_epochs: int = 51

    # Orbit projection parameters
    orbit_basis_dim: int = 64
    token_dim: int = 64

    # Experiment control
    seed: int = 1
    device: str = "cpu"

    # Gate thresholds
    gate_threshold: float = 0.60
    stability_threshold: float = 0.10
    eps: float = 1e-8


def get_config(config_path: str = None) -> ExperimentConfig:
    """Load config from YAML file, overriding dataclass defaults."""
    cfg = ExperimentConfig()
    if config_path is None:
        config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            data = yaml.safe_load(f)
        if data:
            for k, v in data.items():
                if hasattr(cfg, k):
                    setattr(cfg, k, type(getattr(cfg, k))(v) if not isinstance(v, type(getattr(cfg, k))) else v)
    return cfg


def setup_dirs(cfg: ExperimentConfig) -> None:
    """Create output directories."""
    Path(cfg.figures_dir).mkdir(parents=True, exist_ok=True)
    Path(cfg.results_dir).mkdir(parents=True, exist_ok=True)
