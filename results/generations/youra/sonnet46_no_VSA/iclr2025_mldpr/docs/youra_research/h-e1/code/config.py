from dataclasses import dataclass, field
from typing import Tuple


@dataclass
class H1Config:
    hf_dataset_id: str = "pwc-archive/evaluation-tables"
    panel_path: str = "h_e2_panel.csv"
    output_csv: str = "h_e2_panel_with_diversity.csv"
    figures_dir: str = "figures"
    seed: int = 1

    fuzzy_threshold: int = 85
    n_benchmarks: int = 87

    g0_coverage_min: float = 0.80
    g1_partial_r2_min: float = 0.01
    g2_partial_r2_min: float = 0.01
    g3_std_min: float = 0.10
    g4_vif_warn: float = 5.0
    g4_vif_max: float = 10.0
    collinearity_r_max: float = 0.95


@dataclass
class FigureConfig:
    dpi: int = 150
    fig_size_single: Tuple[float, float] = (8, 5)
    fig_size_wide: Tuple[float, float] = (12, 5)
    fig_size_square: Tuple[float, float] = (7, 6)

    color_pass: str = "#2ecc71"
    color_fail: str = "#e74c3c"
    color_neutral: str = "#3498db"
    color_warn: str = "#f39c12"

    corr_palette: str = "coolwarm"
    corr_vmin: float = -1.0
    corr_vmax: float = 1.0

    font_size_title: int = 13
    font_size_label: int = 11
    font_size_tick: int = 9

    fname_gate_metrics: str = "gate_metrics.png"
    fname_coverage_heatmap: str = "coverage_heatmap.png"
    fname_predictor_distributions: str = "predictor_distributions.png"
    fname_correlation_matrix: str = "correlation_matrix.png"
    fname_partial_r2: str = "partial_r2.png"


CFG = H1Config()
FIG_CFG = FigureConfig()
