"""Config: H-M2 Layer-wise Probe Sweep."""

from dataclasses import dataclass, field
import random
import numpy as np
import torch


@dataclass
class Config:
    seed: int = 42
    model_name: str = "meta-llama/Meta-Llama-3-8B-Instruct"
    torch_dtype: str = "float16"
    device_map: str = "auto"
    num_layers: int = 32
    hidden_dim: int = 4096

    # 8 layer depths: 12.5% -> 100%
    layer_depths: list = field(
        default_factory=lambda: [0.125, 0.25, 0.375, 0.5, 0.6, 0.75, 0.875, 1.0]
    )
    # Gate comparison layers
    early_depth: float = 0.25
    middle_depth: float = 0.6
    final_depth: float = 1.0

    n_train: int = 500
    n_val: int = 200
    max_new_tokens: int = 32

    lr: float = 1e-2
    weight_decay: float = 1e-4
    epochs: int = 15
    batch_size: int = 256
    extraction_batch_size: int = 32

    n_bootstrap: int = 1000

    figures_dir: str = "figures/"
    outputs_dir: str = "outputs/"


def get_layer_indices(num_layers: int, depths: list) -> list:
    """Depth fraction -> 0-indexed layer index. For 32 layers: [3,7,11,15,18,23,27,31]."""
    return [max(0, int(d * num_layers) - 1) for d in depths]


def set_seed(seed: int = 42) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


CFG = Config()
LAYER_INDICES = get_layer_indices(CFG.num_layers, CFG.layer_depths)
