from dataclasses import dataclass
import random
import numpy as np
import torch


@dataclass
class Config:
    seed: int = 42
    model_name: str = "meta-llama/Meta-Llama-3-8B-Instruct"
    torch_dtype: str = "bfloat16"
    device_map: str = "auto"
    target_layer: int = 19
    hidden_dim: int = 4096
    dataset_name: str = "trivia_qa"
    dataset_config: str = "rc"
    train_size: int = 9500
    val_size: int = 1700
    max_new_tokens: int = 32
    lr: float = 1e-3
    epochs: int = 10
    batch_size: int = 256
    optimizer: str = "adam"
    loss: str = "bce"
    auroc_gate: float = 0.60
    auroc_baseline: float = 0.50
    figures_dir: str = "figures/"
    cache_dir: str = "cache/"


def set_seed(seed: int = 42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


CFG = Config()
