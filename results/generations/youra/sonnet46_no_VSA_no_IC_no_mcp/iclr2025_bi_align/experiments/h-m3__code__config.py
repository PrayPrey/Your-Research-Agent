"""H-M3 configuration: OLS regression slope significance test."""
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ExperimentConfig:
    # Input
    input_csv_path: str = "docs/youra_research/h-m2/results/h_m2_normalized_gap.csv"
    required_columns: list = field(default_factory=lambda: ["kl_budget", "gap"])
    min_n: int = 5

    # Regression
    n_boot: int = 10_000
    random_seed: int = 42

    # Output
    figures_dir: str = "docs/youra_research/h-m3/figures"
    results_dir: str = "docs/youra_research/h-m3/results"
    results_json_path: str = "docs/youra_research/h-m3/results/h_m3_results.json"

    # Visualization
    figure_dpi: int = 150

    # Gate thresholds
    gate_slope_min: float = 0.0
    gate_p_max: float = 0.05
    gate_r2_min: float = 0.5

    def validate(self) -> None:
        if not Path(self.input_csv_path).exists():
            raise FileNotFoundError(
                f"H-M2 output CSV not found: {self.input_csv_path}\n"
                "Ensure H-M2 Phase 4 has been completed successfully."
            )


def load_config() -> ExperimentConfig:
    return ExperimentConfig()
