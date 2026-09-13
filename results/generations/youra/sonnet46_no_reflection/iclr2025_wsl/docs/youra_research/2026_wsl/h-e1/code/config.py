from dataclasses import dataclass, field
from typing import List
import yaml
import os


@dataclass
class ExperimentConfig:
    # Data paths (relative to code/ directory)
    cnn_zoo_dir: str = "data/cnn_zoo/"
    transformer_zoo_dir: str = "data/transformer_zoo/"
    figures_dir: str = "figures/"
    results_path: str = "outputs/results.json"

    # Checkpoint counts
    n_cnn_checkpoints: int = 200
    n_transformer_checkpoints: int = 250  # 250 MNIST (no AG-News available)

    # Permutation settings
    n_permutations: int = 10
    perm_seeds: List[int] = field(default_factory=lambda: list(range(10)))

    # Evaluation settings
    sample_seed: int = 42
    eval_batch_size: int = 256

    # Gate threshold
    delta_acc_threshold: float = 0.001

    # Device
    device: str = "cuda"


def load_config(config_path: str = None) -> ExperimentConfig:
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
                    setattr(cfg, k, v)
    return cfg
