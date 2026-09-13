"""Seed Independence Tester Module."""

import os
import sys
import torch
import torch.nn as nn
import numpy as np
from typing import Dict
from pathlib import Path

# Add h-e1 code path for model imports
h_e1_path = Path(__file__).parent.parent.parent / "h-e1" / "code"
sys.path.insert(0, str(h_e1_path))

from model import SimpleMLP1Layer, SimpleMLP2Layer


def setup_determinism(seed: int) -> None:
    """
    Enable full PyTorch determinism for seed independence testing.

    Based on: https://pytorch.org/docs/stable/notes/randomness.html

    Args:
        seed: Random seed for all RNG sources
    """
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    os.environ['CUBLAS_WORKSPACE_CONFIG'] = ':16:8'


def initialize_model_with_seed(architecture: str, seed: int, device: str = "cuda") -> nn.Module:
    """
    Initialize model with specific seed for deterministic weight initialization.

    Args:
        architecture: '1layer' or '2layer'
        seed: Random seed for initialization
        device: Device to place model on

    Returns:
        Initialized model with seed-controlled weights

    Raises:
        ValueError: If architecture is unknown
    """
    setup_determinism(seed)

    if architecture == "1layer":
        model = SimpleMLP1Layer()
    elif architecture == "2layer":
        model = SimpleMLP2Layer()
    else:
        raise ValueError(f"Unknown architecture: {architecture}")

    model = model.to(device)
    return model


def extract_parameters(model: nn.Module) -> torch.Tensor:
    """
    Flatten all model parameters into single tensor.

    Args:
        model: PyTorch model

    Returns:
        Flattened parameter tensor [num_params]
    """
    params = torch.cat([p.flatten().cpu() for p in model.parameters()])
    return params


def run_seed_independence_test(
    architecture: str,
    seeds: list,
    device: str = "cuda"
) -> Dict[int, torch.Tensor]:
    """
    Initialize models with different seeds and extract parameters.

    Args:
        architecture: '1layer' or '2layer'
        seeds: List of random seeds
        device: Device to use

    Returns:
        Dictionary mapping seed -> flattened parameters
    """
    models_dict = {}

    for seed in seeds:
        model = initialize_model_with_seed(architecture, seed, device)
        params = extract_parameters(model)
        models_dict[seed] = params

        # Clean up to save memory
        del model
        torch.cuda.empty_cache() if torch.cuda.is_available() else None

    return models_dict
