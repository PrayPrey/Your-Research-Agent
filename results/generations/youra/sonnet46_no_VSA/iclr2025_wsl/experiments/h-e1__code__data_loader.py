"""ModelZooDataset CIFAR10-GS loader and state dict reconstruction."""
import sys
import os
import json
import torch
import numpy as np
from copy import deepcopy

# Inject ModelZooDataset deserialization module
_MODELZOO_CODE = "/tmp/modelzoo_repo/code"
if os.path.isdir(_MODELZOO_CODE) and _MODELZOO_CODE not in sys.path:
    sys.path.insert(0, _MODELZOO_CODE)

# Actual CIFAR10-GS CNN architecture (from ModelZooDataset inspection)
# 3 conv layers + 2 FC layers
# Channels: conv1=(8 out, 3 in), conv2=(6 out, 8 in), conv3=(4 out, 6 in)
# kernels: 5x5, 5x5, 2x2
CONV_WEIGHT_KEYS = [
    "module_list.0.weight",  # (8, 3, 5, 5)
    "module_list.3.weight",  # (6, 8, 5, 5)
    "module_list.6.weight",  # (4, 6, 2, 2)
]
CONV_BIAS_KEYS = [
    "module_list.0.bias",    # (8,)
    "module_list.3.bias",    # (6,)
    "module_list.6.bias",    # (4,)
]
FC_WEIGHT_KEYS = [
    "module_list.9.weight",  # (20, 36)
    "module_list.11.weight", # (10, 20)
]
FC_BIAS_KEYS = [
    "module_list.9.bias",    # (20,)
    "module_list.11.bias",   # (10,)
]
CNN_LAYER_NAMES = CONV_WEIGHT_KEYS + CONV_BIAS_KEYS + FC_WEIGHT_KEYS + FC_BIAS_KEYS

# Per conv layer: weight_dim = C_in * kH * kW
# conv1: 3*5*5=75, conv2: 8*5*5=200, conv3: 6*2*2=24
LAYER_WEIGHT_DIMS = [75, 200, 24]
CHANNELS_PER_LAYER = [8, 6, 4]  # C_out per conv layer


def load_dataset(pt_path: str, split: str = "testset", n_models: int = 100) -> list:
    """
    Load ModelZooDataset .pt file.
    Returns list of state_dicts (OrderedDicts) for the first n_models.
    """
    data = torch.load(pt_path, map_location="cpu", weights_only=False)
    ds = data[split]
    n = min(n_models, len(ds))
    models = [ds[i] for i in range(n)]
    accs = list(ds.properties["test_acc"][:n])
    print(f"Loaded {n} models from {split} (total={len(ds)}). "
          f"Accuracy range: [{min(accs):.3f}, {max(accs):.3f}]")
    return models, accs


def reconstruct_state_dict(state_dict: dict) -> dict:
    """Return a copy of the state_dict (already in correct format)."""
    return deepcopy(state_dict)


def load_index_dict(json_path: str) -> dict:
    """Load index_dict.json if available, else return None."""
    if json_path and os.path.exists(json_path):
        with open(json_path) as f:
            return json.load(f)
    return None
