"""BenchmarkConfig for H-M1: Orbit-PE timing benchmark."""
from dataclasses import dataclass
import yaml
import os


@dataclass
class BenchmarkConfig:
    cnn_zoo_dir: str = "data/cnn_zoo/"
    transformer_zoo_dir: str = "data/transformer_zoo/"
    transformer_mnist_dir: str = "data/transformer_zoo/mnist/"
    figures_dir: str = "figures/"
    results_path: str = "outputs/results.json"

    n_cnn_checkpoints: int = 100
    n_transformer_checkpoints: int = 100
    n_transformer_mnist: int = 100

    sample_seed: int = 42
    token_dim: int = 64
    orbit_embed_dim: int = 64
    overhead_threshold: float = 1.2
    device: str = "cpu"


def load_config(config_path: str = None) -> BenchmarkConfig:
    """Load config from YAML file, overriding dataclass defaults."""
    cfg = BenchmarkConfig()
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
