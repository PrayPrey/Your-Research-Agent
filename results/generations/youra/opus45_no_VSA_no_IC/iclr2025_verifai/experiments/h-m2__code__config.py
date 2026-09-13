from dataclasses import dataclass
import os

_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

@dataclass(frozen=True)
class Config:
    h_m1_data_path: str = os.path.join(_BASE, "../h-m1/code/results/h_m1_data.csv")
    results_dir: str = "results"
    figures_dir: str = "figures"
    weight_grid_step: float = 0.1
    weight_min: float = 0.1
    weight_max: float = 0.9
    max_r_individual: float = 0.873
    alpha: float = 0.05
    seed: int = 42

CONFIG = Config()
