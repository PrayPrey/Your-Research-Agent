"""Configuration for H-M1 Seed Independence Experiment."""

from dataclasses import dataclass, field
from typing import List
from pathlib import Path


@dataclass
class ExperimentConfig:
    """Configuration for seed independence testing."""

    # Experimental design
    seeds: List[int] = field(default_factory=lambda: list(range(30)))
    architectures: List[str] = field(default_factory=lambda: ["1layer", "2layer"])
    datasets: List[str] = field(default_factory=lambda: ["mnist", "fashion_mnist"])

    # Device settings
    device: str = "cuda"

    # Paths
    data_root: str = "./data"
    output_dir: str = "./results"
    figures_dir: str = "./figures"

    def __post_init__(self):
        """Ensure output directories exist."""
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        Path(self.figures_dir).mkdir(parents=True, exist_ok=True)


@dataclass
class DeterminismConfig:
    """PyTorch determinism configuration."""

    cublas_workspace_config: str = ":16:8"
    cudnn_deterministic: bool = True
    cudnn_benchmark: bool = False


def get_default_config() -> ExperimentConfig:
    """Return default experiment configuration."""
    return ExperimentConfig()
