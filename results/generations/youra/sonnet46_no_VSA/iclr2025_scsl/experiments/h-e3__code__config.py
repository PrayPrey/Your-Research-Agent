import os
import random
import numpy as np
import torch
from dataclasses import dataclass, field

DATA_ROOT = "/home/PrayPrey/data/waterbirds_v1.0/waterbirds_v1.0/"
CKPT_DIR = "docs/youra_research/h-e3/results/checkpoints/"
RESULTS_PATH = "docs/youra_research/h-e3/results/h_e3_results.json"
FIGURES_DIR = "docs/youra_research/h-e3/figures/"

LR = 3e-3
MOMENTUM = 0.9
WEIGHT_DECAY = 1e-4
BATCH_SIZE = 32
N_EPOCHS = 50
CHECKPOINT_EPOCHS = [0, 1, 5, 10, 20, 50]
SEEDS = [1, 2, 3, 4, 5]
PILOT_SEED = 1
PILOT_EPOCHS = 5
K_HUTCHINSON = 50
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

MINORITY_GROUPS = (1, 3)  # landbird on water, waterbird on land
MAJORITY_GROUPS = (0, 2)
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def ensure_dirs() -> None:
    os.makedirs(CKPT_DIR, exist_ok=True)
    os.makedirs(FIGURES_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(RESULTS_PATH), exist_ok=True)


def ckpt_path(seed: int, epoch: int) -> str:
    return os.path.join(CKPT_DIR, f"ckpt_seed{seed}_epoch{epoch}.pt")
