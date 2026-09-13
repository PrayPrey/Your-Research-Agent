"""Experiment configuration for h-m1."""
import random
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch


@dataclass
class ExperimentConfig:
    seed: int = 42
    epochs: int = 5  # ponytail: minimal for CPU PoC; scale up with GPU
    batch_size: int = 128
    lr: float = 0.1
    momentum: float = 0.9
    weight_decay: float = 5e-4
    checkpoint_every: int = 5

    data_root: str = "/home/PrayPrey/ai_scientist/experiments_sonnet46_0/2026-05-14_08-19-11_training_data_forensics_from_weights_attempt_0/0-run/process_SpawnProcess-8/data"
    ckpt_dir: str = "./h-m1/checkpoints"
    fig_dir: str = "./h-m1/figures"

    probes_per_mode: int = 100  # ponytail: minimal for CPU PoC
    modes: tuple = ("mem", "transfer", "spurious")

    trak_proj_dim: int = 2048
    trak_use_half_precision: bool = True

    tracin_num_checkpoints: int = 1
    kronfluence_use_amp: bool = True


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
