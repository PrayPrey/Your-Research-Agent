"""Configuration for H-M1: Hook Non-Intrusiveness Verification."""

from dataclasses import dataclass
import random
import numpy as np
import torch


@dataclass
class Config:
    seed: int = 42
    model_name: str = "meta-llama/Meta-Llama-3-8B-Instruct"
    torch_dtype: str = "float16"
    device_map: str = "auto"
    target_layer: int = 19
    n_samples: int = 500
    max_new_tokens: int = 128
    identity_gate: float = 1.0
    overhead_gate_pct: float = 10.0
    figures_dir: str = "figures/"
    cache_dir: str = "cache/"
    outputs_dir: str = "outputs/"


def set_seed(seed: int = 42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


CFG = Config()
