"""Configuration for H-M2 Trajectory Divergence Analysis."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class TrainingConfig:
    """Configuration for training models to generate trajectory data."""

    n_seeds: int = 30
    n_epochs: int = 10
    batch_size: int = 64
    learning_rate: float = 0.01
    momentum: float = 0.9

    # Device settings
    device: str = "cuda"

    # Conditions (using MNIST only due to Fashion-MNIST mirror issues)
    architectures: List[str] = field(
        default_factory=lambda: ["1layer", "2layer"]
    )
    datasets: List[str] = field(
        default_factory=lambda: ["mnist", "mnist_alt"]
    )

    @property
    def conditions(self) -> List[str]:
        """Generate condition names from architectures × datasets."""
        return [
            f"{arch}_{dataset}"
            for arch in self.architectures
            for dataset in self.datasets
        ]


@dataclass
class AnalysisConfig:
    """Configuration for trajectory divergence analysis."""

    # Training settings
    training: TrainingConfig = field(default_factory=TrainingConfig)

    # Output paths
    output_dir: Path = field(default_factory=lambda: Path("./results"))
    figures_dir: Path = field(default_factory=lambda: Path("./figures"))
    data_cache: Path = field(default_factory=lambda: Path("./.data_cache"))

    # Statistical testing thresholds
    primary_alpha: float = 0.05
    secondary_cv_threshold: float = 1.0

    def __post_init__(self):
        """Ensure output directories exist."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.figures_dir.mkdir(parents=True, exist_ok=True)
        self.data_cache.mkdir(parents=True, exist_ok=True)


def get_default_config() -> AnalysisConfig:
    """Return default analysis configuration."""
    return AnalysisConfig()
