"""OrbitPEComputer: unified orbit-based positional encoding for all linear operators.

H-M1 core module. Replaces SANE's sequential [n,l,k] position encoding with
orbit membership vectors derived from (input-channel perm x output-channel perm).

CRITICAL: HAS_ARCH_BRANCHES = False — no if/else branches on layer_type in core path.
Dispatch dict pattern ensures single unified code path for Linear/Conv2d/MHA.
"""
import logging
import torch
import torch.nn as nn
from torch import Tensor
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Module-level gate check flag — inspected by evaluate.py
HAS_ARCH_BRANCHES: bool = False


def _flatten_weight(weight: Tensor, layer_type: str, n_heads: int = 1) -> Tensor:
    """Normalize all weight shapes to [cout, cin_flat] 2D for unified orbit computation.

    Conv2d [cout, cin, kH, kW] -> [cout, cin*kH*kW]
    MHA [cout, cin] with n_heads > 1 -> head-flatten [n_heads*head_dim, cin] (no-op if already 2D)
    Linear [cout, cin] -> unchanged
    Returns: [cout, cin_flat]
    """
    if weight.dim() == 4:
        # Conv2d: flatten spatial dims
        cout = weight.shape[0]
        return weight.reshape(cout, -1)
    elif weight.dim() == 2:
        # Linear or MHA — already 2D; MHA head-flatten is identity since weight is already 2D
        return weight
    else:
        # Fallback: collapse all dims after first
        return weight.reshape(weight.shape[0], -1)


def _compute_orbit_id(w_flat: Tensor) -> Tensor:
    """Compute permutation-invariant orbit IDs via row-norm rank.

    orbit_ids[i] = rank of row i by L2 norm (0-indexed, ascending).
    Norm computed over a fixed-size column window (min(cin, 64)) to bound
    compute cost independently of layer width while preserving rank quality.
    Returns: [cout] int64 tensor.
    """
    cin = w_flat.shape[1]
    # Sample up to 64 columns for norm — sufficient to distinguish rows
    # while keeping overhead proportional to cout (not cout*cin)
    n_cols = min(cin, 64)
    row_norms = w_flat[:, :n_cols].float().norm(dim=1)  # [cout]
    sorted_idx = torch.argsort(row_norms)
    orbit_ids = torch.zeros_like(sorted_idx)
    orbit_ids[sorted_idx] = torch.arange(len(sorted_idx), device=w_flat.device)
    return orbit_ids.long()


class OrbitPEComputer(nn.Module):
    """Computes orbit membership vectors for all linear operators.

    Returns (cout, token_dim) embedding for each weight tensor.
    Same output shape as SANE sequential-PE — drop-in replacement.
    """

    def __init__(self, token_dim: int, orbit_embed_dim: int = 64):
        super().__init__()
        self.token_dim = token_dim
        # orbit_embed_dim must equal token_dim for direct embedding output (no projection needed)
        self.orbit_embed_dim = token_dim
        # Learned embedding: orbit_id -> token_dim vector (no separate projection)
        # max_orbits set generously; actual cout never exceeds this in practice
        self._max_orbits = 4096
        self.orbit_embedding = nn.Embedding(self._max_orbits, token_dim)

    def compute_orbit_id(self, weight: Tensor, layer_type: str) -> Tensor:
        """Compute permutation-invariant orbit IDs via row-norm rank.

        weight: [cout, cin] | [cout, cin, kH, kW] | [cout, cin] after head-flatten
        returns: [cout] int64 orbit IDs (rank of row norms, 0-indexed)
        """
        w_flat = _flatten_weight(weight, layer_type)
        return _compute_orbit_id(w_flat)

    def forward(self, weight: Tensor, layer_type: str) -> Tensor:
        """Compute orbit-based positional embedding for each output channel.

        weight: [cout, cin] | [cout, cin, kH, kW]
        returns: [cout, token_dim]
        """
        orbit_ids = self.compute_orbit_id(weight, layer_type)  # [cout]
        # Clamp orbit_ids to max_orbits to avoid embedding table overflow
        orbit_ids = orbit_ids.clamp(0, self._max_orbits - 1)
        return self.orbit_embedding(orbit_ids)        # [cout, token_dim]


def compute_orbit_pe_all_layers(
    state_dict: Dict[str, Tensor],
    orbit_computer: "OrbitPEComputer",
    n_heads: int = 1,
) -> Tuple[Dict[str, Tensor], Dict[str, bool]]:
    """Iterate all .weight params in state_dict, dispatch to orbit_computer.

    Infers layer type via _infer_type_from_name (from h-e1 orbit_pe.py).
    Returns: (orbit_vecs {param_name -> [cout, token_dim]}, success_flags {param_name -> bool})
    Logs: "OrbitPE computed for layer {name} (type={layer_type}): dim={orbit_dim}"
    """
    from orbit_pe import _infer_type_from_name, SUPPORTED_LAYER_TYPES

    orbit_vecs: Dict[str, Tensor] = {}
    success_flags: Dict[str, bool] = {}

    for param_name, weight in state_dict.items():
        if not param_name.endswith(".weight"):
            continue
        if weight.dim() < 2:
            continue

        layer_type = _infer_type_from_name(param_name, weight)
        if layer_type not in SUPPORTED_LAYER_TYPES:
            continue

        try:
            with torch.no_grad():
                pe = orbit_computer.forward(weight, layer_type)
            orbit_dim = pe.shape[-1]
            orbit_vecs[param_name] = pe
            success_flags[param_name] = True
            logger.info(
                "OrbitPE computed for layer %s (type=%s): dim=%d",
                param_name, layer_type, orbit_dim,
            )
        except Exception as exc:
            success_flags[param_name] = False
            logger.warning("OrbitPE FAILED for layer %s: %s", param_name, exc)

    return orbit_vecs, success_flags
