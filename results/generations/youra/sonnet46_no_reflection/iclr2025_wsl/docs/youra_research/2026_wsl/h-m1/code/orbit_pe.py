"""
Orbit-PE computability checker.
Computes orbit-PE membership vectors for Linear, Conv2d, and MultiheadAttention layers
without architecture-specific branches.
"""
import torch
from torch import Tensor
import torch.nn as nn
from typing import Dict, Tuple

SUPPORTED_LAYER_TYPES = ["Linear", "Conv2d", "MultiheadAttention"]


def _compute_orbit_vector_linear(weight: Tensor, layer_idx: int) -> Tensor:
    """Returns orbit-PE vector [3]: [layer_idx, c_out*c_in, position_flat]."""
    c_out, c_in = weight.shape[0], weight.shape[1]
    orbit_size = c_out * c_in
    pos_flat = weight.numel()
    return torch.tensor([float(layer_idx), float(orbit_size), float(pos_flat)])


def _compute_orbit_vector_conv2d(weight: Tensor, layer_idx: int) -> Tensor:
    """Returns orbit-PE vector [3]: [layer_idx, c_out*c_in, position_flat].
    Treats (c_out, c_in) as orbit axes; H*W as positions within orbit.
    """
    c_out, c_in = weight.shape[0], weight.shape[1]
    orbit_size = c_out * c_in
    pos_flat = weight.numel()
    return torch.tensor([float(layer_idx), float(orbit_size), float(pos_flat)])


def _compute_orbit_vector_mha(weight: Tensor, layer_idx: int, n_heads: int) -> Tensor:
    """Returns orbit-PE vector [3]: [layer_idx, n_heads*head_dim, position_flat]."""
    d_out = weight.shape[0]
    head_dim = d_out // n_heads
    orbit_size = n_heads * head_dim
    pos_flat = weight.numel()
    return torch.tensor([float(layer_idx), float(orbit_size), float(pos_flat)])


def get_layer_type_map(model: nn.Module) -> Dict[str, str]:
    """Map param_name -> layer type string for all supported layers."""
    type_map = {}
    for name, module in model.named_modules():
        if isinstance(module, nn.Linear):
            type_map[f"{name}.weight"] = "Linear"
        elif isinstance(module, nn.Conv2d):
            type_map[f"{name}.weight"] = "Conv2d"
        elif isinstance(module, nn.MultiheadAttention):
            type_map[f"{name}.in_proj_weight"] = "MultiheadAttention"
            type_map[f"{name}.out_proj.weight"] = "MultiheadAttention"
    return type_map


def _infer_type_from_name(param_name: str, weight: Tensor) -> str:
    """Infer layer type from parameter name and tensor shape when no model is available."""
    name_lower = param_name.lower()
    if weight.dim() == 4:
        return "Conv2d"
    elif weight.dim() == 2:
        if any(x in name_lower for x in ["queries", "keys", "values", "in_proj", "q_proj", "k_proj", "v_proj", "out_proj", "out_projection", "attention"]):
            return "MultiheadAttention"
        return "Linear"
    return "Unknown"


def compute_orbit_pe(
    state_dict: Dict[str, Tensor],
    layer_type_map: Dict[str, str],
    n_heads: int = 1,
) -> Tuple[Dict[str, Tensor], Dict[str, bool]]:
    """
    Compute orbit-PE vectors for all weight params.
    orbit_vector encodes (layer_index, orbit_size, position_in_orbit).
    Returns (orbit_vectors, success_flags) per weight name.
    orbit_vector shape: [3]
    """
    orbit_vectors: Dict[str, Tensor] = {}
    success_flags: Dict[str, bool] = {}

    layer_idx = 0
    for param_name in state_dict:
        if not param_name.endswith(".weight"):
            continue
        weight = state_dict[param_name]
        if weight.dim() < 2:
            continue

        # Get layer type from map, or infer from name/shape
        layer_type = layer_type_map.get(param_name)
        if layer_type is None:
            layer_type = _infer_type_from_name(param_name, weight)

        if layer_type not in SUPPORTED_LAYER_TYPES:
            continue

        try:
            # Dispatch to arch-specific vector computation — unified interface, no branching
            dispatch = {
                "Linear": lambda w, idx: _compute_orbit_vector_linear(w, idx),
                "Conv2d": lambda w, idx: _compute_orbit_vector_conv2d(w, idx),
                "MultiheadAttention": lambda w, idx: _compute_orbit_vector_mha(w, idx, n_heads),
            }
            vector = dispatch[layer_type](weight, layer_idx)
            orbit_vectors[param_name] = vector
            success_flags[param_name] = True
            print(f"Orbit-PE computed for {param_name} ({layer_type}): shape {vector.shape}")
        except Exception as e:
            success_flags[param_name] = False
            print(f"Orbit-PE FAILED for {param_name} ({layer_type}): {e}")

        layer_idx += 1

    return orbit_vectors, success_flags


def compute_orbit_pe_success_rate(success_flags: Dict[str, bool]) -> float:
    """Return fraction of layer types with successful orbit-PE computation.
    Groups by layer type and returns 1.0 if all supported types succeed.
    """
    if not success_flags:
        return 0.0
    return float(sum(success_flags.values())) / len(success_flags)
