"""Configuration for H-M2: NFN Equivariant Encoder Permutation Sensitivity Probing."""
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple

import numpy as np
import torch

MNIST_CNN_WEIGHT_SHAPES: List[tuple] = [
    (8, 1, 5, 5),    # conv1.weight  (actual hyp_rand zoo)
    (8,),             # conv1.bias
    (6, 8, 5, 5),    # conv2.weight
    (6,),             # conv2.bias
    (4, 6, 2, 2),    # conv3.weight
    (4,),             # conv3.bias
    (20, 36),         # fc1.weight
    (20,),            # fc1.bias
    (10, 20),         # fc2.weight
    (10,),            # fc2.bias
]


@dataclass
class ExperimentConfig:
    # Paths
    data_dir: Path = Path("../../.data_cache/datasets/mnist_hyp_rand")
    he1_code_dir: Path = Path("../../h-e1/code")
    hm1_code_dir: Path = Path("../../h-m1/code")
    results_dir: Path = Path("./results")
    figures_dir: Path = Path("./figures")
    zoo_name: str = "mnist_cnn_hyp_rand"

    # Training (same as h-m1)
    seed: int = 42
    epochs: int = 150
    batch_size: int = 32
    lr: float = 1e-3
    weight_decay: float = 1e-4
    betas: Tuple[float, float] = (0.9, 0.999)
    t_max: int = 150
    eta_min: float = 1e-6

    # NFN model
    embed_dim: int = 128
    weight_shapes: List[tuple] = field(default_factory=lambda: MNIST_CNN_WEIGHT_SHAPES)
    channel_dim_candidates: List[int] = field(default_factory=lambda: [96, 112, 128, 144, 160])
    n_layers_candidates: List[int] = field(default_factory=lambda: [2, 3, 4])
    target_params_min: int = 475_000
    target_params_max: int = 525_000

    # Probing
    n_pairs: int = 500
    min_pairs: int = 50
    acc_threshold: float = 0.01
    sensitivity_gate_absolute: float = 0.1
    sensitivity_gate_relative: float = 0.3245   # flat_MLP_score(0.6490) * 0.5
    flat_mlp_sensitivity_score: float = 0.6490  # from h-m1
    spearman_target: float = 0.1041             # from h-m1

    def __post_init__(self):
        self.data_dir = Path(self.data_dir)
        self.he1_code_dir = Path(self.he1_code_dir)
        self.hm1_code_dir = Path(self.hm1_code_dir)
        self.results_dir = Path(self.results_dir)
        self.figures_dir = Path(self.figures_dir)


@dataclass
class VisualizationConfig:
    figure_size: tuple = (10, 6)
    dpi: int = 150
    figures_dir: Path = Path("./figures")

    def __post_init__(self):
        self.figures_dir = Path(self.figures_dir)


def set_seed(seed: int) -> None:
    """Set all random seeds for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
