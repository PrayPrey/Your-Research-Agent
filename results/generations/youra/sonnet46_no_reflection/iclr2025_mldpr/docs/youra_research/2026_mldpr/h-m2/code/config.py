"""H-M2: ExperimentConfig dataclass + YAML loader."""
import os
import yaml
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ExperimentConfig:
    hm1_code_path: str = "../h-m1/code"
    dataset_id: str = "pwc-archive/evaluation-tables"
    min_submissions: int = 20
    min_quarters: int = 8
    date_start: str = "2018-01-01"
    date_end: str = "2025-12-31"
    domains: List[str] = field(default_factory=lambda: ["cv", "nlp", "tabular"])
    domain_thresholds: Dict[str, float] = field(
        default_factory=lambda: {"cv": 0.5, "nlp": 0.3, "tabular": 0.90}
    )
    bootstrap_iters: int = 100
    seed: int = 42
    tau_threshold: float = 0.90
    min_consecutive: int = 2
    r1_tau_threshold: float = 0.85
    min_collapse_events: int = 20
    min_lead_months: int = 12
    gate_fraction_threshold: float = 0.60
    gate_min_domains: int = 2
    rolling_quarters: int = 4
    significance_level: float = 0.05
    output_dir: str = "../figures"
    results_json: str = "../results.json"
    results_csv: str = "outputs/results.csv"
    figure_dpi: int = 150
    figure_size: tuple = (10, 6)
    domain_colors: Dict[str, str] = field(
        default_factory=lambda: {"cv": "#2196F3", "nlp": "#FF5722", "tabular": "#4CAF50"}
    )
    ablation_variants: List[str] = field(
        default_factory=lambda: ["A1", "A2", "A3", "A4", "A5"]
    )


def load_config(yaml_path: str) -> ExperimentConfig:
    """Load ExperimentConfig from YAML override file."""
    with open(yaml_path, "r") as f:
        data = yaml.safe_load(f)
    cfg = ExperimentConfig()
    for k, v in data.items():
        if hasattr(cfg, k):
            setattr(cfg, k, v)
    return cfg
