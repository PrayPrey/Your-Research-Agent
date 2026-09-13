"""ExperimentConfig dataclass for H-E1 permutation orbit analysis."""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class ExperimentConfig:
    data_dir: Path = Path("./data/model_zoo")
    results_dir: Path = Path("./results")
    figures_dir: Path = Path("./figures")
    zoo_name: str = "mnist_cnn"
    seed: int = 42
    n_per_decile: int = 50
    n_deciles: int = 10
    acc_threshold: float = 0.01
    cosine_dist_threshold: float = 0.1
    orbit_proportion_gate: float = 0.05
    bn_verify_sample_size: int = 5

    def __post_init__(self):
        self.data_dir = Path(self.data_dir)
        self.results_dir = Path(self.results_dir)
        self.figures_dir = Path(self.figures_dir)

    @property
    def n_pairs(self) -> int:
        return self.n_per_decile * self.n_deciles


@dataclass
class VisualizationConfig:
    figure_size: tuple = (10, 6)
    dpi: int = 150
    colormap: str = "tab10"
