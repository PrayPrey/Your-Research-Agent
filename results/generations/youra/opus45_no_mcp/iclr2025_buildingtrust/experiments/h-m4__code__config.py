"""H-M4 Configuration: Hedging-Confidence Correlation Analysis."""
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple


@dataclass
class H_M4_Config:
    """Configuration for H-M4 correlation analysis."""

    hypothesis_id: str = "H-M4"
    hypothesis_type: str = "MECHANISM"

    h_m2_cache_path: Path = field(default_factory=lambda: Path(__file__).parent.parent.parent / "h-m2/code/results/h-m2_results.json")
    output_dir: Path = field(default_factory=lambda: Path(__file__).parent / "results")
    figures_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent / "figures")

    gate_r_threshold: float = -0.2
    gate_p_threshold: float = 0.05
    min_samples: int = 500

    alpha: float = 0.05
    n_bootstrap: int = 1000
    bootstrap_seed: int = 42

    hedging_buckets: List[Tuple[int, int]] = field(default_factory=lambda: [(0, 0), (1, 2), (3, 5), (6, 999)])
    figure_dpi: int = 150
    figure_format: str = "png"

    def __post_init__(self):
        self.h_m2_cache_path = Path(self.h_m2_cache_path)
        self.output_dir = Path(self.output_dir)
        self.figures_dir = Path(self.figures_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.figures_dir.mkdir(parents=True, exist_ok=True)
