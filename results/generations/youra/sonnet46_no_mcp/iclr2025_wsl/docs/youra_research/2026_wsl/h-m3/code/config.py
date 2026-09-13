import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple, Optional

import numpy as np
import torch


TRAINING_MODE = {
    "mnist_cnn": {
        "FlatMLP":   "checkpoint_load",
        "DeepSets":  "train_fresh",
        "NFN":       "checkpoint_load",
    },
    "cifar10": {
        "FlatMLP":   "train_fresh",
        "DeepSets":  "train_fresh",
        "NFN":       "train_fresh",
    },
}

CHECKPOINT_PATHS = {
    "FlatMLP": "../h-m1/code/results/best_flat_mlp_encoder.pt",
    "NFN":     "../h-m2/code/results/best_nfn_encoder.pt",
}

OPTIMIZER_DEFAULTS = {
    "lr": 1e-3,
    "weight_decay": 1e-4,
    "betas": (0.9, 0.999),
}

SCHEDULER_DEFAULTS = {
    "T_max": 150,
    "eta_min": 1e-6,
}

OUTPUT_FILES = {
    "results_json":         "results/h-m3_results.json",
    "fig_rho_bar":          "figures/rho_comparison.png",
    "fig_symmetry_spectrum":"figures/symmetry_spectrum.png",
    "fig_tier_delta_rho":   "figures/tier_delta_rho.png",
    "fig_bootstrap_dist":   "figures/bootstrap_dist.png",
    "fig_cross_zoo":        "figures/cross_zoo.png",
}


@dataclass
class ExperimentConfig:
    # Paths (absolute, resolved relative to this file's location)
    mnist_data_dir: Path = Path(__file__).parent.parent.parent / ".data_cache/datasets/mnist_hyp_rand"
    cifar_data_dir: Path = Path(__file__).parent.parent.parent / ".data_cache/datasets/cifar10_hyp_rand"
    hm1_code_dir: Path = Path(__file__).parent.parent.parent / "h-m1/code"
    hm2_code_dir: Path = Path(__file__).parent.parent.parent / "h-m2/code"
    results_dir: Path = Path(__file__).parent / "results"
    figures_dir: Path = Path(__file__).parent / "figures"

    # Training (Deep Sets + CIFAR-10 retraining)
    seed: int = 42
    epochs: int = 150
    batch_size: int = 32
    lr: float = 1e-3
    weight_decay: float = 1e-4
    betas: Tuple[float, float] = (0.9, 0.999)
    t_max: int = 150
    eta_min: float = 1e-6

    # Deep Sets capacity search
    embed_dim: int = 128
    phi_hidden_candidates: List[int] = field(
        default_factory=lambda: [64, 96, 128, 160, 192, 256]
    )
    rho_hidden: int = 256
    target_params_min: int = 475_000
    target_params_max: int = 525_000

    # Bootstrap
    n_resamples: int = 1000

    # Gate thresholds
    delta_rho_mnist_threshold: float = 0.05
    delta_rho_cifar_threshold: float = 0.0

    # Device
    device: str = "auto"

    def __post_init__(self):
        self.mnist_data_dir = Path(self.mnist_data_dir)
        self.cifar_data_dir = Path(self.cifar_data_dir)
        self.hm1_code_dir = Path(self.hm1_code_dir)
        self.hm2_code_dir = Path(self.hm2_code_dir)
        self.results_dir = Path(self.results_dir)
        self.figures_dir = Path(self.figures_dir)
        if self.device == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"


@dataclass
class VisualizationConfig:
    figure_size_bar: tuple = (10, 6)
    figure_size_delta: tuple = (8, 5)
    figure_size_bootstrap: tuple = (12, 4)
    figure_size_cross_zoo: tuple = (10, 6)
    figure_size_spectrum: tuple = (10, 4)
    dpi: int = 150
    style: str = "seaborn-v0_8-whitegrid"
    encoder_colors: dict = None
    figures_dir: Path = Path("./figures")

    def __post_init__(self):
        self.figures_dir = Path(self.figures_dir)
        if self.encoder_colors is None:
            self.encoder_colors = {
                "FlatMLP":  "#4C72B0",
                "DeepSets": "#DD8452",
                "NFN":      "#55A868",
            }


@dataclass
class RunConfig:
    skip_cifar_if_unavailable: bool = True
    run_train: bool = True
    run_evaluate: bool = True
    run_visualize: bool = True
    run_gate_check: bool = True
    log_level: str = "INFO"
    log_to_file: bool = True
    log_file: Path = Path("./results/run.log")

    def __post_init__(self):
        self.log_file = Path(self.log_file)


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
