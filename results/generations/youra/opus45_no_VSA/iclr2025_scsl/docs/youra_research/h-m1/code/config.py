from dataclasses import dataclass
from typing import Tuple

@dataclass
class Config:
    seed: int = 0
    lr: float = 1e-3
    momentum: float = 0.9
    weight_decay: float = 1e-4
    batch_size: int = 128
    epochs: int = 50
    step_size: int = 10
    gamma: float = 0.1
    num_workers: int = 4
    image_size: int = 224
    num_classes: int = 2
    majority_groups: Tuple[int, ...] = (0, 3)
    minority_groups: Tuple[int, ...] = (1, 2)
    device: str = "cpu"  # ponytail: fallback to CPU due to cuDNN init issue; switch back when driver fixed
    data_root: str = "./data/waterbirds"
    results_dir: str = "./outputs"

@dataclass
class AnalysisConfig:
    max_lag: int = 5
    confidence: float = 0.95
    n_bootstrap: int = 10000

SEEDS = [0, 1, 2, 3, 4]
IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)

def set_seed(seed: int) -> None:
    import random
    import numpy as np
    import torch
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
