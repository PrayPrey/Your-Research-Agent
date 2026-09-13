import re
import sys
import torch
import numpy as np
from collections import OrderedDict
import config

sys.path.insert(0, config.MZDATASET_CODE_PATH)


def _sort_keys_numerically(keys: list) -> list:
    return sorted(keys, key=lambda k: [int(x) if x.isdigit() else x for x in re.split(r'(\d+)', k)])


def load_zoo_models(n: int = config.N_MODELS, seed: int = config.SEED) -> list:
    """Load N random state_dicts from CIFAR-10 zoo testset."""
    data = torch.load(config.ZOO_PT_PATH, map_location="cpu", weights_only=False)
    testset = data["testset"]
    total = len(testset)
    rng = np.random.default_rng(seed)
    indices = rng.choice(total, size=min(n, total), replace=False)
    return [testset[int(i)] for i in indices]


def get_weight_dim(state_dicts: list) -> int:
    """Compute flat weight dimension from first state_dict."""
    sd = state_dicts[0]
    return sum(v.numel() for v in sd.values())


def detect_hidden_layers(state_dict: dict) -> list:
    """Return weight keys for hidden layers (exclude first and last weight layers)."""
    weight_keys = _sort_keys_numerically([k for k in state_dict if k.endswith(".weight")])
    if len(weight_keys) <= 2:
        return []
    return weight_keys[1:-1]
