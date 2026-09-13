"""Test MLP generator for H-M1 permutation invariance test."""

import torch
from typing import Dict, Tuple


def generate_test_mlp(
    hidden_dims: Tuple[int, ...] = (32, 32),
    input_dim: int = 32,
    output_dim: int = 10,
    seed: int = 42,
) -> Dict[str, torch.Tensor]:
    """Generate random MLP state_dict with layer{i}.weight/bias keys.

    Matches H-E1's actual checkpoint architecture (32-32-32-10).
    """
    torch.manual_seed(seed)

    dims = [input_dim] + list(hidden_dims) + [output_dim]
    state_dict = {}

    for i in range(len(dims) - 1):
        W = torch.randn(dims[i + 1], dims[i]) * 0.1
        b = torch.zeros(dims[i + 1])
        state_dict[f"layer{i}.weight"] = W
        state_dict[f"layer{i}.bias"] = b

    return state_dict
