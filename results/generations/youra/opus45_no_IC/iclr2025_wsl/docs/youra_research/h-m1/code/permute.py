"""Permutation generation and application for H-M1."""

import torch
from copy import deepcopy
from typing import Dict, List, Tuple


def generate_permutations(
    hidden_dims: Tuple[int, ...] = (32, 32),
    base_seed: int = 0
) -> List[torch.Tensor]:
    """Generate one randperm per hidden layer."""
    torch.manual_seed(base_seed)
    return [torch.randperm(h) for h in hidden_dims]


def permute_state_dict(
    state_dict: Dict[str, torch.Tensor],
    n_hidden_layers: int = 2,
    perms: List[torch.Tensor] = None,
) -> Dict[str, torch.Tensor]:
    """Apply neuron permutations to state_dict.

    Hidden layer i:
      - Output rows permuted by perms[i]
      - Input cols permuted by perms[i-1] (if i > 0)
    Final output layer:
      - Input cols permuted by perms[-1]
      - No output row permutation (preserve class order)
    """
    new_sd = deepcopy(state_dict)

    for i in range(n_hidden_layers):
        W = new_sd[f"layer{i}.weight"].clone()
        b = new_sd[f"layer{i}.bias"].clone()

        W = W[perms[i], :]
        b = b[perms[i]]

        if i > 0:
            W = W[:, perms[i - 1]]

        new_sd[f"layer{i}.weight"] = W
        new_sd[f"layer{i}.bias"] = b

    W_out = new_sd[f"layer{n_hidden_layers}.weight"].clone()
    new_sd[f"layer{n_hidden_layers}.weight"] = W_out[:, perms[-1]]

    return new_sd
