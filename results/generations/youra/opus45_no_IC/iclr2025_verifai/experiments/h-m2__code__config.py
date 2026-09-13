from dataclasses import dataclass
import os
import random
import numpy as np
import torch


@dataclass
class ExperimentConfig:
    model_id: str = "bigcode/starcoder2-3b"
    dataset_id: str = "s2e-lab/SecurityEval"
    temperature: float = 0.2
    max_new_tokens: int = 512
    max_iterations: int = 5
    analysis_timeout_s: int = 30
    seed: int = 1
    device: str = "cuda"
    output_dir: str = "results"
    figures_dir: str = "figures"


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def ensure_dirs(config: ExperimentConfig) -> None:
    os.makedirs(config.output_dir, exist_ok=True)
    os.makedirs(config.figures_dir, exist_ok=True)


def results_path(config: ExperimentConfig, filename: str) -> str:
    return os.path.join(config.output_dir, filename)
