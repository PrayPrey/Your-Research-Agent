"""Configuration for H-E1 Benchmark Fingerprint Detection."""
from dataclasses import dataclass, field
from pathlib import Path
import torch
import numpy as np
import random


@dataclass
class Config:
    # data
    benchmarks: list = field(default_factory=lambda: ["cub", "dogs", "flowers", "cars", "aircraft"])
    probe_dataset: str = "nabirds"
    data_root: str = "./data"
    num_workers: int = 4

    # reproducibility
    seeds: list = field(default_factory=lambda: [0, 1, 2])

    # finetuning
    epochs: int = 30
    lr: float = 0.01
    batch_size: int = 32
    weight_decay: float = 1e-4
    momentum: float = 0.9

    # model
    feature_dim: int = 2048
    pretrained: bool = True

    # linear probe
    probe_C: float = 1.0
    probe_max_iter: int = 1000
    train_split: float = 0.70
    val_split: float = 0.15
    test_split: float = 0.15

    # stats
    cv_folds: int = 3
    bootstrap_resamples: int = 1000
    chance_accuracy: float = 0.20

    # paths
    ckpt_dir: str = "./models/finetuned"
    feature_dir: str = "./features"
    results_path: str = "./results/h_e1_results.json"
    figure_path: str = "./figures/confusion_matrix.png"

    def __post_init__(self):
        for d in [self.ckpt_dir, self.feature_dir,
                  str(Path(self.results_path).parent),
                  str(Path(self.figure_path).parent)]:
            Path(d).mkdir(parents=True, exist_ok=True)


def set_seed(seed: int):
    """Set random seed for reproducibility."""
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    random.seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
