"""Configuration for H-M1 experiment.

Extends H-E1 config with:
- 6-encoder registry (ENCODER_CONFIG, ENCODER_NAMES, AUG_APPLY_PROB)
- GateConfig for dual-condition MUST_WORK gate (delta_rho + delta_r2)
- VizConfig for 5-figure visualization suite
- ExperimentConfig for multi-seed orchestration
"""
from dataclasses import dataclass, field
from typing import List

# ---------------------------------------------------------------------------
# Multi-seed / severity constants
# ---------------------------------------------------------------------------
SEEDS: List[int] = [42, 123, 456]
SEVERITY_LEVELS: List[float] = [0.0, 0.25, 0.5, 1.0]

# ---------------------------------------------------------------------------
# 6-Encoder registry (C-1-1)
# ---------------------------------------------------------------------------
ENCODER_NAMES: List[str] = [
    "flat-MLP",
    "flat-MLP+aug",
    "flat-MLP+canon",
    "NFT-base",
    "NFT+aug",
    "Oracle-canon",
]

ENCODER_CONFIG: dict = {
    "flat-MLP":       {"aug_severity": None,  "canon": False,       "model_type": "flat"},
    "flat-MLP+aug":   {"aug_severity": 1.0,   "canon": False,       "model_type": "flat"},
    "flat-MLP+canon": {"aug_severity": None,  "canon": "l2_norm",   "model_type": "flat"},
    "NFT-base":       {"aug_severity": None,  "canon": False,       "model_type": "nft"},
    "NFT+aug":        {"aug_severity": 1.0,   "canon": False,       "model_type": "nft"},
    "Oracle-canon":   {"aug_severity": None,  "canon": "oracle",    "model_type": "flat"},
}

# aug_severity=1.0 applied at this probability during training batches
AUG_APPLY_PROB: float = 0.5

# ---------------------------------------------------------------------------
# Path constants (C-1-2)
# ---------------------------------------------------------------------------
DATA_PATH: str = "data/unterthiner_mnist_zoo.pkl"
RESULTS_DIR: str = "results/"
FIGURES_DIR: str = "figures/"
CHECKPOINT_DIR: str = "checkpoints/"

# ---------------------------------------------------------------------------
# DataConfig (H-E1 verbatim — C-1-2)
# ---------------------------------------------------------------------------
@dataclass
class DataConfig:
    dataset_url: str = "https://storage.googleapis.com/gresearch/dnn_predict_accuracy/small_mnist_networks.pkl"
    local_path: str = "data/unterthiner_mnist_zoo.pkl"
    min_samples: int = 500
    train_ratio: float = 0.8
    batch_size: int = 64
    seed: int = 42
    severity_levels: List[float] = field(default_factory=lambda: [0.0, 0.25, 0.5, 1.0])


# ---------------------------------------------------------------------------
# Model configs (H-E1 verbatim)
# ---------------------------------------------------------------------------
@dataclass
class NFTModelConfig:
    d_model: int = 128
    n_heads: int = 4
    n_layers: int = 2
    dropout: float = 0.0


@dataclass
class FlatMLPConfig:
    hidden_dim: int = 512
    n_hidden_layers: int = 3
    activation: str = "ReLU"


@dataclass
class TrainConfig:
    optimizer: str = "Adam"
    lr: float = 1e-3
    betas: tuple = (0.9, 0.999)
    weight_decay: float = 1e-4
    scheduler: str = "CosineAnnealingLR"
    T_max: int = 100
    eta_min: float = 1e-5
    batch_size: int = 64
    n_epochs: int = 100
    seed: int = 42
    nan_recovery_lr: float = 1e-4


# ---------------------------------------------------------------------------
# GateConfig — H-M1 dual-condition MUST_WORK gate (C-5-1)
# ---------------------------------------------------------------------------
@dataclass
class GateConfig:
    nft_delta_rho_threshold: float = 0.02
    mediation_delta_r2_threshold: float = 0.10
    aug_partial_delta_rho_min: float = 0.05
    aug_partial_delta_rho_max: float = 0.10
    flat_mlp_delta_rho_threshold: float = 0.10
    gate_result_path: str = "results/gate_result.json"


# ---------------------------------------------------------------------------
# VizConfig — 5-figure visualization suite (C-6-1, C-6-2)
# ---------------------------------------------------------------------------
@dataclass
class VizConfig:
    figures_dir: str = "figures/"
    dpi: int = 150
    fig_format: str = "png"
    bar_figsize: tuple = (10, 6)
    curve_figsize: tuple = (10, 6)
    mediation_figsize: tuple = (8, 5)
    heatmap_figsize: tuple = (10, 6)
    bootstrap_figsize: tuple = (10, 5)
    style: str = "seaborn-v0_8-whitegrid"
    palette: str = "tab10"
    gate_line_color: str = "red"
    gate_line_style: str = "--"
    gate_line_alpha: float = 0.8
    fig1_name: str = "fig1_delta_rho_bar.png"
    fig2_name: str = "fig2_delta_rho_curves.png"
    fig3_name: str = "fig3_mediation_bar.png"
    fig4_name: str = "fig4_rho_heatmap.png"
    fig5_name: str = "fig5_bootstrap_dist.png"


# ---------------------------------------------------------------------------
# ExperimentConfig — multi-seed orchestration (C-7-1)
# ---------------------------------------------------------------------------
@dataclass
class ExperimentConfig:
    seeds: List[int] = field(default_factory=lambda: [42, 123, 456])
    encoder_names: List[str] = field(default_factory=lambda: list(ENCODER_NAMES))

    # Training (inherited from H-E1 — verified field names)
    lr: float = 1e-3
    betas: tuple = (0.9, 0.999)
    weight_decay: float = 1e-4
    scheduler: str = "CosineAnnealingLR"
    T_max: int = 100
    eta_min: float = 1e-5
    batch_size: int = 64
    n_epochs: int = 100
    nan_recovery_lr: float = 1e-4

    # Evaluation
    n_bootstrap: int = 10000
    alpha: float = 0.05
    severity_levels: List[float] = field(default_factory=lambda: [0.0, 0.25, 0.5, 1.0])

    # Sanity check
    sanity_n_samples: int = 10

    # Run flags
    run_sanity_check: bool = True
    run_training: bool = True
    run_evaluation: bool = True
    run_visualization: bool = True

    # Paths
    data_path: str = "data/unterthiner_mnist_zoo.pkl"
    results_dir: str = "results/"
    figures_dir: str = "figures/"
    checkpoint_dir: str = "checkpoints/"
    results_file: str = "results/h-m1_results.json"

    # Device
    device: str = "cuda"
