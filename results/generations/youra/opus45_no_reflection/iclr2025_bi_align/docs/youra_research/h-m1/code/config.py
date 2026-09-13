"""BiDPO training configuration for H-M1."""
from dataclasses import dataclass
import os
import random
import numpy as np
import torch


@dataclass
class BiDPOConfig:
    seed: int = 42
    model_name: str = "mistralai/Mistral-7B-Instruct-v0.2"
    dtype: str = "bfloat16"
    device_map: str = "auto"
    dataset_name: str = "Anthropic/hh-rlhf"
    max_length: int = 1024
    beta: float = 0.1
    lambda_agency: float = 0.5
    agency_clip_max: float = 5.0
    learning_rate: float = 5e-7
    batch_size: int = 1
    grad_accum_steps: int = 16
    epochs: int = 1
    warmup_ratio: float = 0.1
    grad_clip_norm: float = 1.0
    lr_schedule: str = "cosine"
    log_interval: int = 100
    output_dir: str = "outputs/"
    figures_dir: str = "outputs/figures/"
    results_path: str = "outputs/results.json"


CONFIG = BiDPOConfig()

GATE = {
    "max_nan_inf_allowed": 0,
    "require_loss_decrease": True,
}


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def ensure_dirs() -> None:
    os.makedirs(CONFIG.output_dir, exist_ok=True)
    os.makedirs(CONFIG.figures_dir, exist_ok=True)
