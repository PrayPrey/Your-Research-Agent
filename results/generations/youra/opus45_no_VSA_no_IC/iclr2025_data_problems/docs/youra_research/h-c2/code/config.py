"""Experiment configuration for h-c2 cross-model mode profile transfer."""
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict

import numpy as np
import torch


@dataclass
class ExperimentConfig:
    seed: int = 42
    batch_size: int = 128
    checkpoint_every: int = 3
    trak_proj_dim: int = 1024  # ponytail: reduced for CPU
    trak_use_half_precision: bool = False  # CPU doesn't benefit from half
    probes_per_mode: int = 50  # ponytail: minimal for CPU PoC
    modes: tuple = ("mem", "transfer", "spurious")
    r_threshold: float = 0.7
    bonferroni_alpha: float = 0.05 / 3
    n_boot: int = 500
    probe_subset_fraction: float = 0.5
    min_test_accuracy: float = 0.60  # ponytail: relaxed for short CPU training
    data_root: str = "/home/PrayPrey/.cache/torch/datasets"
    ckpt_dir: str = "/home/PrayPrey/YOURA_no_VSA_no_IC/opus45/TEST_data_problems/docs/youra_research/h-c2/checkpoints"
    fig_dir: str = "/home/PrayPrey/YOURA_no_VSA_no_IC/opus45/TEST_data_problems/docs/youra_research/h-c2/figures"
    kronfluence_use_amp: bool = False


@dataclass
class ModelTrainConfig:
    name: str
    epochs: int
    lr: float
    optimizer: str


MODEL_CONFIGS: Dict[str, ModelTrainConfig] = {
    "resnet18": ModelTrainConfig(name="resnet18", epochs=1, lr=0.01, optimizer="sgd"),
    "vit_small": ModelTrainConfig(name="vit_small", epochs=1, lr=3e-4, optimizer="adamw"),
    "convnext_tiny": ModelTrainConfig(name="convnext_tiny", epochs=1, lr=3e-4, optimizer="adamw"),
}


def set_all_seeds(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False


def setup_dirs(cfg: ExperimentConfig) -> None:
    Path(cfg.ckpt_dir).mkdir(parents=True, exist_ok=True)
    Path(cfg.fig_dir).mkdir(parents=True, exist_ok=True)
    Path(cfg.data_root).mkdir(parents=True, exist_ok=True)
