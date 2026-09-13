"""Configuration for H-M3 Non-Monotonicity Analysis."""
from dataclasses import dataclass

H_M1_RESULTS_PATH: str = "../../h-m1/code/results/repair_results.json"


@dataclass
class AnalysisConfig:
    """Configuration for H-M3 statistical reanalysis."""

    # Data source (path relative to h-m3/code/)
    h_m1_results_path: str = H_M1_RESULTS_PATH

    # Statistical thresholds
    equivalence_margin: float = 0.02  # H-M3 gate: G4 <= G3 + 2%
    alpha: float = 0.05
    confidence: float = 0.95

    # Output paths
    results_dir: str = "results"
    figures_dir: str = "figures"
    output_contingency: str = "results/contingency_table.json"
    output_stats: str = "results/statistical_tests.yaml"
    output_metrics: str = "results/metrics.yaml"

    # Visualization settings
    fig_width: int = 8
    fig_height: int = 6
    dpi: int = 150
    color_g3: str = "#2ecc71"
    color_g4: str = "#3498db"
    color_threshold: str = "red"
    output_gate_comparison: str = "figures/gate_comparison.png"
    output_contingency_heatmap: str = "figures/contingency_heatmap.png"
    output_confidence_interval: str = "figures/confidence_interval.png"
    output_granularity_curve: str = "figures/granularity_curve.png"
