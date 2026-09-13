"""Configuration for H-E1 Variance Measurement Experiment."""

from dataclasses import dataclass, field
from typing import List, Tuple
from pathlib import Path


@dataclass
class ExperimentConfig:
    """Configuration for variance measurement experiments."""

    # Experimental design
    datasets: List[str] = field(default_factory=lambda: ["mnist", "fashion_mnist"])
    architectures: List[str] = field(default_factory=lambda: ["1layer", "2layer"])
    seeds: List[int] = field(default_factory=lambda: list(range(30)))

    # Training hyperparameters
    epochs: int = 10
    lr: float = 0.01
    momentum: float = 0.9
    batch_size: int = 64

    # Determinism settings
    cudnn_deterministic: bool = True
    cudnn_benchmark: bool = False

    # Paths
    data_root: str = "./data"
    results_dir: str = "./results"
    figures_dir: str = "./figures"

    def get_conditions(self) -> List[Tuple[str, str]]:
        """Get all condition combinations.

        Returns:
            List of (dataset, architecture) tuples
        """
        conditions = []
        for dataset in self.datasets:
            for arch in self.architectures:
                conditions.append((dataset, arch))
        return conditions

    def __post_init__(self):
        """Ensure directories exist."""
        Path(self.data_root).mkdir(parents=True, exist_ok=True)
        Path(self.results_dir).mkdir(parents=True, exist_ok=True)
        Path(self.figures_dir).mkdir(parents=True, exist_ok=True)
