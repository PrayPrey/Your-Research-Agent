"""Load and map ρ_j values from h-m1 to ResNet-50 parameters."""

import torch
import numpy as np
from pathlib import Path
from typing import Dict


def load_rho_j_from_h_m1(config: dict) -> Dict[str, float]:
    """
    Load ρ_j values from h-m1 validation results.

    Args:
        config: Configuration dict with gradient_aware.rho_j_source and fallback_rho

    Returns:
        layer_rho_j: {layer_name: float} mean ρ_j per layer
    """
    rho_j_path = Path(config['gradient_aware']['rho_j_source'])

    # Try loading from .npy file
    if rho_j_path.exists():
        try:
            rho_dict = np.load(rho_j_path, allow_pickle=True).item()
            print(f"Loaded ρ_j from {rho_j_path}")
            return rho_dict
        except Exception as e:
            print(f"Failed to load ρ_j: {e}")

    # Fallback to h-m1 validation report means
    print("Using fallback ρ_j from h-m1 validation report")
    return config['gradient_aware']['fallback_rho']


def map_rho_j_to_resnet50_params(
    rho_j_dict: Dict[str, float],
    model: torch.nn.Module
) -> Dict[str, float]:
    """
    Map layer-wise ρ_j to ResNet-50 parameter names.

    Args:
        rho_j_dict: {layer_name: mean_rho} from h-m1
        model: ResNet-50 model

    Returns:
        param_rho: {param_name: rho_value} for all model parameters
    """
    param_rho = {}

    for name, param in model.named_parameters():
        # Map parameter to layer
        if 'conv1' in name or 'bn1' in name:
            layer_rho = rho_j_dict.get('conv1', 0.0)
        elif 'layer1' in name:
            layer_rho = rho_j_dict.get('layer1', 0.0)
        elif 'layer2' in name:
            layer_rho = rho_j_dict.get('layer2', 0.0)
        elif 'layer3' in name:
            layer_rho = rho_j_dict.get('layer3', 0.0)
        elif 'layer4' in name:
            layer_rho = rho_j_dict.get('layer4', 0.0)
        else:
            # Final layer (task-specific) - no spurious correlation
            layer_rho = 0.0

        param_rho[name] = layer_rho

    print(f"Mapped ρ_j to {len(param_rho)} parameters")
    return param_rho
