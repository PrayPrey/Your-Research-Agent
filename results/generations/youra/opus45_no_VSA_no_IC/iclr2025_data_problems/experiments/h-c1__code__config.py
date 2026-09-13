"""Configuration for h-c1: Mode Profile Reliability Analysis."""
from dataclasses import dataclass
import os


@dataclass
class Config:
    npz_path: str = "../../h-m1/code/h-m1/attribution_scores.npz"
    fig_dir: str = "./figures"
    results_path: str = "./gate_results.json"
    methods: tuple = ("trak", "tracin", "kronfluence")
    modes: tuple = ("memorization", "feature_transfer", "spurious")
    alpha_threshold: float = 0.8
    min_samples: int = 30  # Minimum for Cronbach's alpha

    def __post_init__(self):
        os.makedirs(self.fig_dir, exist_ok=True)
