from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List
import yaml


@dataclass
class Config:
    # Data source — path relative to code/ working directory
    h_m1_results_path: str = "../../h-m1/code/results/contamination_matrix_wide.csv"

    # Statistical parameters
    alpha: float = 0.05
    seed: int = 1
    min_corpora_directional_confirmed: int = 2

    # Analysis parameters
    top_n: int = 5
    corpora: List[str] = field(default_factory=lambda: ["pile", "c4", "redpajama"])

    # Directional predictions per corpus (group_a > group_b expected)
    directional_predictions: dict = field(default_factory=lambda: {
        "pile":      {"group_a_domain": "academic",    "group_b_domain": "commonsense"},
        "c4":        {"group_a_domain": "commonsense", "group_b_domain": "academic"},
        "redpajama": {"group_a_domain": "academic",    "group_b_domain": "commonsense"},
    })

    # Output paths
    results_dir: str = "results"
    figures_dir: str = "figures"

    # Figure settings
    figure_dpi: int = 150
    figure_format: str = "png"


def load_config() -> Config:
    """Load config with optional YAML override via H_M2_CONFIG_PATH env var."""
    cfg = Config()
    path = os.environ.get("H_M2_CONFIG_PATH")
    if path and os.path.exists(path):
        with open(path) as f:
            data = yaml.safe_load(f)
        if data:
            for k, v in data.items():
                if hasattr(cfg, k):
                    setattr(cfg, k, v)
    return cfg
