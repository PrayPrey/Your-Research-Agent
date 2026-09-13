"""Configuration constants and dataclasses for h-m1 experiment."""
from dataclasses import dataclass, field
import random
import numpy as np
import torch

MODEL_SIZES: list[str] = ["1b", "2.8b", "6.9b", "12b"]
MODEL_PARAMS: dict[str, float] = {"1b": 1e9, "2.8b": 2.8e9, "6.9b": 6.9e9, "12b": 12e9}
MODEL_HF_IDS: dict[str, str] = {
    "1b": "EleutherAI/pythia-1b",
    "2.8b": "EleutherAI/pythia-2.8b",
    "6.9b": "EleutherAI/pythia-6.9b",
    "12b": "EleutherAI/pythia-12b",
}
RANKS: list[int] = [4, 8, 16, 32, 64, 128]
MAX_SEQ_LEN: int = 512
SEED: int = 42


@dataclass
class TrainConfig:
    epochs: int = 3
    lr: float = 1e-4
    batch_size: int = 4
    grad_accum: int = 4
    warmup_ratio: float = 0.1
    lora_alpha_multiplier: int = 2
    lora_dropout: float = 0.05
    lora_target_modules: list[str] = field(default_factory=lambda: ["query_key_value"])


@dataclass
class DataConfig:
    train_n: int = 5000
    val_n: int = 1000
    max_len: int = MAX_SEQ_LEN
    dataset_name: str = "squad_v2"


@dataclass
class ModelLoadConfig:
    torch_dtype: str = "float16"
    device_map: str = "auto"
    cache_dir: str = "./model_cache"
    trust_remote_code: bool = False


def set_seed(seed: int = SEED) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
