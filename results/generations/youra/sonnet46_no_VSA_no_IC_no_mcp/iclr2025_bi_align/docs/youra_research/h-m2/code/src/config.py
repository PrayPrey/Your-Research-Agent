from dataclasses import dataclass, field
from pathlib import Path
import yaml


@dataclass
class ExperimentConfig:
    input_csv_path: str = "../../h-m1/results/h_m1_divergence_curve.csv"
    figures_dir: str = "docs/youra_research/h-m2/figures"
    results_dir: str = "docs/youra_research/h-m2/results"
    results_filename: str = "h_m2_results.json"
    gap_csv: str = "h_m2_normalized_gap.csv"
    figure_dpi: int = 150
    high_kl_min_positive: int = 3

    def validate(self) -> None:
        p = Path(self.input_csv_path)
        if not p.exists():
            raise FileNotFoundError(f"Input CSV not found: {self.input_csv_path}")

    @property
    def results_json_path(self) -> str:
        return str(Path(self.results_dir) / self.results_filename)

    @property
    def gap_csv_path(self) -> str:
        return str(Path(self.results_dir) / self.gap_csv)


def load_config(path: str = "config.yaml") -> ExperimentConfig:
    cfg = ExperimentConfig()
    if Path(path).exists():
        with open(path) as f:
            overrides = yaml.safe_load(f) or {}
        for k, v in overrides.items():
            if hasattr(cfg, k):
                setattr(cfg, k, v)
    return cfg
