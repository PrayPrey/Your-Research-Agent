"""ExperimentConfig for H-M1: Flat MLP Encoder Permutation Sensitivity Probing."""
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple

import numpy as np
import torch


@dataclass
class ExperimentConfig:
    # Paths
    data_dir: Path = Path("../../.data_cache/datasets/mnist_hyp_rand")
    he1_code_dir: Path = Path("../../h-e1/code")
    results_dir: Path = Path("./results")
    figures_dir: Path = Path("./figures")
    zoo_name: str = "mnist_cnn_hyp_rand"

    # Training
    seed: int = 42
    epochs: int = 150
    batch_size: int = 32
    lr: float = 1e-3
    weight_decay: float = 1e-4
    betas: Tuple[float, float] = (0.9, 0.999)
    t_max: int = 150
    eta_min: float = 1e-6

    # Model
    embed_dim: int = 128
    dropout: float = 0.1
    target_params_min: int = 475_000
    target_params_max: int = 525_000
    hidden_dims_candidates: List[List[int]] = field(default_factory=lambda: [
        [193], [192], [194], [195], [190], [9], [10], [8, 256], [8, 512], [16, 128], [16, 256]
    ])

    # Probing
    n_pairs: int = 500
    min_pairs: int = 50
    acc_threshold: float = 0.01
    sensitivity_gate: float = 0.3
    spearman_target: float = 0.5

    def __post_init__(self):
        self.data_dir = Path(self.data_dir)
        self.he1_code_dir = Path(self.he1_code_dir)
        self.results_dir = Path(self.results_dir)
        self.figures_dir = Path(self.figures_dir)


@dataclass
class VisualizationConfig:
    figure_size: tuple = (10, 6)
    dpi: int = 150
    colormap: str = "tab10"
    figures_dir: Path = Path("./figures")

    def __post_init__(self):
        self.figures_dir = Path(self.figures_dir)


def set_seed(seed: int) -> None:
    """Set random seeds for torch, numpy, python random."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
