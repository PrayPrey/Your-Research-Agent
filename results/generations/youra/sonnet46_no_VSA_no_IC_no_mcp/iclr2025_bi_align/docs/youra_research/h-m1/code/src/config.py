"""H-M1: ExperimentConfig dataclass and YAML loader."""
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class ExperimentConfig:
    coste_csv_path: str = "data/coste_digitized.csv"
    gao_csv_path: str = "data/gao_digitized.csv"

    figures_dir: str = "docs/youra_research/h-m1/figures"
    results_dir: str = "docs/youra_research/h-m1/results"
    results_filename: str = "h_m1_results.json"
    divergence_csv: str = "h_m1_divergence_curve.csv"

    min_kl_levels: int = 5
    monotonicity_rho_threshold: float = 0.8
    p_value_threshold: float = 0.05
    peak_kl_min: float = 1.0
    peak_kl_max: float = 9.0
    divergence_min: float = 0.0

    figure_dpi: int = 150
    random_seed: int = 1

    def validate(self) -> None:
        p = Path(self.coste_csv_path)
        if not p.exists():
            raise FileNotFoundError(f"Required input not found: {p}")

    @property
    def results_json_path(self) -> str:
        return str(Path(self.results_dir) / self.results_filename)

    @property
    def divergence_csv_path(self) -> str:
        return str(Path(self.results_dir) / self.divergence_csv)


def load_config(path: str = "config.yaml") -> ExperimentConfig:
    cfg_path = Path(path)
    if not cfg_path.exists():
        return ExperimentConfig()
    with open(cfg_path) as f:
        data = yaml.safe_load(f) or {}
    valid_keys = ExperimentConfig.__dataclass_fields__
    return ExperimentConfig(**{k: v for k, v in data.items() if k in valid_keys})
