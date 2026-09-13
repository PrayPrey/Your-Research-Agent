"""Configuration for H-M2: G3 Superiority Over Minimal Feedback Analysis."""

from dataclasses import dataclass, field
from typing import Tuple
import os


@dataclass
class Config:
    """Configuration for H-M2 statistical analysis."""

    # Paths (relative to code/ directory)
    h_m1_results_path: str = "../../h-m1/results/repair_results.json"
    results_dir: str = "results"
    figures_dir: str = "../figures"

    # Statistical Thresholds
    difference_threshold: float = 0.10  # 10 percentage points
    alpha: float = 0.05

    # Target Conditions
    target_granularities: Tuple[str, str] = ("G0", "G3")
    expected_n_pairs: int = 304

    # Visualization
    figure_dpi: int = 150
    figure_size: Tuple[int, int] = (8, 6)
    colors: dict = field(default_factory=lambda: {
        "G0": "#2ecc71",
        "G3": "#e74c3c",
        "threshold": "#f39c12",
        "success": "#27ae60",
        "fail": "#c0392b"
    })

    def __post_init__(self):
        """Create output directories if they don't exist."""
        os.makedirs(self.results_dir, exist_ok=True)
        os.makedirs(self.figures_dir, exist_ok=True)


@dataclass
class GateConfig:
    """Gate configuration for H-M2 hypothesis."""

    gate_type: str = "SHOULD_WORK"
    difference_threshold: float = 0.10
    alpha: float = 0.05
    expected_result: str = "FAIL"

    # Gate condition: G3 >= G0 + 10pp AND McNemar p < 0.05 favoring G3
    condition_description: str = "G3 achieves >= 10pp higher success rate than G0"
