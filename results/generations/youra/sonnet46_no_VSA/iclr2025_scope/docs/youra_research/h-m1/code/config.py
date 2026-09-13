from dataclasses import dataclass, field
from typing import List


@dataclass
class Config:
    # --- Data ---
    teacher_model_id: str = "meta-llama/Llama-3.1-8B"
    dataset_id: str = "allenai/c4"
    dataset_subset: str = "en"
    dataset_split: str = "validation"
    n_samples: int = 500
    target_lengths: List[int] = field(default_factory=lambda: [512, 1024, 2048, 4096, 8192])
    seed: int = 42

    # --- Model dimensions (match LLaMA-3-8B) ---
    n_layers: int = 32
    d_model: int = 4096
    d_state: int = 64
    n_heads: int = 32
    headdim: int = 128  # d_model // n_heads

    # --- SSD Fitter ---
    n_opt_steps: int = 10000
    lr: float = 1e-3
    adam_betas: tuple = (0.9, 0.999)
    adam_weight_decay: float = 0.0
    teacher_dtype: str = "bfloat16"
    fitter_dtype: str = "float32"

    # --- Gate thresholds ---
    gate_slope_threshold: float = 0.5
    gate_pct90_threshold: float = 0.3

    # --- Paths ---
    results_dir: str = "results"
    figures_dir: str = "figures"
    checkpoint_every_n_samples: int = 50


# --- Visualization constants ---
FIGURE_DPI: int = 150
COLOR_SSD: str = "#2196F3"
COLOR_TOEPLITZ: str = "#FF5722"
COLOR_THRESHOLD: str = "#F44336"
COLOR_PALETTE_VIOLIN: str = "Blues"

FIGURE_SIZE_BAR_LOGLOG: tuple = (12, 5)
FIGURE_SIZE_SCALING: tuple = (8, 6)
FIGURE_SIZE_VIOLIN: tuple = (14, 6)
FIGURE_SIZE_HEATMAP: tuple = (10, 4)


@dataclass
class GatePlotConfig:
    figsize: tuple = (12, 5)
    dpi: int = 150
    bar_color: str = "#2196F3"
    threshold_color: str = "#F44336"
    threshold_value: float = 0.3
    xlabel_bar: str = "Sequence Length N"
    ylabel_bar: str = "90th Pct Frobenius Error"
    xlabel_loglog: str = "log N"
    ylabel_loglog: str = "log Mean Frobenius Error"
    out_filename: str = "fig1_gate_bar_loglog.png"


@dataclass
class ScalingPlotConfig:
    figsize: tuple = (8, 6)
    dpi: int = 150
    color_ssd: str = "#2196F3"
    color_toeplitz: str = "#FF5722"
    xlabel: str = "Sequence Length N (log scale)"
    ylabel: str = "Mean Frobenius Error (log scale)"
    out_filename: str = "fig2_scaling_ssd_vs_toeplitz.png"


@dataclass
class ViolinPlotConfig:
    figsize: tuple = (14, 6)
    dpi: int = 150
    palette: str = "Blues"
    threshold_color: str = "#F44336"
    threshold_value: float = 0.3
    xlabel: str = "Sequence Length N"
    ylabel: str = "Frobenius Error"
    out_filename: str = "fig3_violin_distribution.png"


@dataclass
class HeatmapPlotConfig:
    figsize: tuple = (10, 4)
    dpi: int = 150
    cmap: str = "viridis"
    xlabel: str = "Layer Index"
    ylabel: str = "Mean Frobenius Error"
    title: str = "Per-Layer Frobenius Error at N=8192"
    out_filename: str = "fig4_layer_heatmap.png"
