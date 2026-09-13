"""Configuration for H-M3 Bootstrap CI Stability Analysis.

Task: T-EPIC-01 (A-1: Configuration Setup)
"""

from dataclasses import dataclass, field
from typing import List
from pathlib import Path


@dataclass
class BootstrapConfig:
    """Configuration for bootstrap variance CI analysis."""

    # Bootstrap parameters
    n_resamples: int = 1000
    confidence_level: float = 0.95
    ci_width_threshold_pct: float = 50.0
    random_seed: int = 42

    # Data loading (from h-e1 artifacts)
    h_e1_results_path: str = "../../h-e1/code/results/experiment_logs.csv"
    conditions: List[str] = field(default_factory=lambda: [
        "1layer_mnist",
        "1layer_fashion_mnist",
        "2layer_mnist",
        "2layer_fashion_mnist"
    ])

    # Output paths
    results_dir: str = "./results"
    figures_dir: str = "./figures"

    # Visualization settings
    dpi: int = 300
    figsize_distributions: tuple = (12, 10)
    figsize_ci_width: tuple = (10, 6)
    figsize_scatter: tuple = (10, 6)

    def __post_init__(self):
        """Ensure directories exist."""
        Path(self.results_dir).mkdir(parents=True, exist_ok=True)
        Path(self.figures_dir).mkdir(parents=True, exist_ok=True)
