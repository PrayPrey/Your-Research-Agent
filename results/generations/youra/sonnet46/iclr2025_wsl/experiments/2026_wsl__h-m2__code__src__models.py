"""Model definitions for H-M1 experiment.

6 encoder variants for mechanism analysis:
E1: FlatMLPEncoder        — baseline flat MLP (ported from H-E1)
E2: FlatMLPAugEncoder     — flat MLP + permutation augmentation
E3: FlatMLPCanonEncoder   — flat MLP + L2 normalization canonicalization
E4: NFTEquivariantEncoder — NFT equivariant encoder (ported from H-E1)
E5: NFTAugEncoder         — NFT + permutation augmentation
E6: OracleCanonEncoder    — flat MLP + oracle sort canonicalization

Factory: build_encoder(encoder_name, flat_input_dim, layer_fan_ins)
"""
import logging
import random

import numpy as np
import torch
import torch.nn as nn
from torch import Tensor

from src.config import AUG_APPLY_PROB, ENCODER_CONFIG

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Augmentation helpers (L-2-2)
# ---------------------------------------------------------------------------

def apply_random_permutation_flat(x: Tensor, severity: float = 1.0, prob: float = AUG_APPLY_PROB) -> Tensor:
    """Apply random permutation augmentation to flat weight vectors.

    With probability `prob` (only during training), permutes `severity` fraction
    of elements in each sample's flat vector.

    Parameters
    ----------
    x : Tensor
        Shape (B, D) — flattened weight vector batch.
    severity : float
        Fraction of elements to permute (default 1.0 = full permutation).
    prob : float
        Probability of applying augmentation per forward call.

    Returns
    -------
    Tensor
        Shape (B, D), possibly with permuted elements.
    """
    if random.random() > prob:
        return x  # No augmentation

    B, D = x.shape
    result = x.clone()
    x_np = x.detach().cpu().numpy()
    n_permute = max(1, int(D * severity))

    for b in range(B):
        perm_idx = np.random.choice(D, size=n_permute, replace=False)
        shuffled = perm_idx[np.random.permutation(n_permute)]
        arr = x_np[b].copy()
        arr[perm_idx] = x_np[b][shuffled]
        result[b] = torch.tensor(arr, dtype=x.dtype, device=x.device)

    return result


def apply_random_permutation_nft(weight_matrices: list, severity: float = 1.0, prob: float = AUG_APPLY_PROB) -> list:
    """Apply random neuron permutation to NFT weight matrix list.

    With probability `prob`, permutes `severity` fraction of neurons per layer.

    Parameters
    ----------
    weight_matrices : list[Tensor]
        Each tensor shape (B, n_units_l, fan_in_l).
    severity : float
        Fraction of neurons to permute.
    prob : float
        Probability of applying augmentation.

    Returns
    -------
    list[Tensor]
        Same shapes, possibly permuted.
    """
    if random.random() > prob:
        return weight_matrices

    result = []
    for wm in weight_matrices:
        B, n_units, fan_in = wm.shape
        wm_np = wm.detach().cpu().numpy()
        stressed = wm_np.copy()
        n_permute = max(1, int(n_units * severity))

        for b in range(B):
            perm_idx = np.random.choice(n_units, size=n_permute, replace=False)
            shuffled = perm_idx[np.random.permutation(n_permute)]
            stressed[b][perm_idx] = wm_np[b][shuffled]

        result.append(torch.tensor(stressed, dtype=wm.dtype, device=wm.device))
    return result


# ---------------------------------------------------------------------------
# Canonicalization helpers (L-2-3)
# ---------------------------------------------------------------------------

def l2_normalize_weights(x: Tensor) -> Tensor:
    """L2-normalize each row of the flat weight vector.

    Treats the flat vector as a sequence of unit vectors by normalizing
    each element w.r.t. the full vector's L2 norm.

    Parameters
    ----------
    x : Tensor
        Shape (B, D).

    Returns
    -------
    Tensor
        Shape (B, D), each row has unit L2 norm.
    """
    norms = x.norm(dim=1, keepdim=True).clamp(min=1e-8)
    return x / norms


def oracle_sort_weights(x: Tensor) -> Tensor:
    """Sort flat weight vector elements by magnitude (descending).

    Provides a deterministic canonical ordering invariant to permutation.

    Parameters
    ----------
    x : Tensor
        Shape (B, D).

    Returns
    -------
    Tensor
        Shape (B, D), elements sorted by descending absolute value.
    """
    sorted_x, _ = torch.sort(x.abs(), dim=1, descending=True)
    # Preserve signs by multiplying sorted abs values by sign of original sorted positions
    # Simple approach: sort by value directly (magnitude-based canonical form)
    sorted_vals, _ = torch.sort(x, dim=1, descending=True)
    return sorted_vals


# ---------------------------------------------------------------------------
# E1: FlatMLPEncoder (ported verbatim from H-E1 — L-2-1)
# ---------------------------------------------------------------------------

class FlatMLPEncoder(nn.Module):
    """3-hidden-layer ReLU MLP for flattened weight vectors (E1).

    Parameters
    ----------
    input_dim : int
        Dimension of flattened weight vector.
    hidden_dim : int
        Width of each hidden layer (default 512).
    """

    def __init__(self, input_dim: int, hidden_dim: int = 512) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
        )
        self.head = nn.Linear(hidden_dim, 1)

        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.kaiming_uniform_(m.weight, nonlinearity="relu")
                if m.bias is not None:
                    nn.init.zeros_(m.bias)

    def forward(self, x: Tensor) -> Tensor:
        """Forward pass. x: (B, input_dim) -> (B, 1)."""
        return self.head(self.net(x))


# ---------------------------------------------------------------------------
# E2: FlatMLPAugEncoder — FlatMLP + augmentation (L-2-2)
# ---------------------------------------------------------------------------

class FlatMLPAugEncoder(nn.Module):
    """FlatMLP with random permutation augmentation during training (E2).

    Augmentation applies at AUG_APPLY_PROB probability, severity=1.0.
    Disabled during eval mode.
    """

    def __init__(self, input_dim: int, hidden_dim: int = 512) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
        )
        self.head = nn.Linear(hidden_dim, 1)
        self.aug_severity = 1.0

        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.kaiming_uniform_(m.weight, nonlinearity="relu")
                if m.bias is not None:
                    nn.init.zeros_(m.bias)

    def forward(self, x: Tensor) -> Tensor:
        """Forward pass with training-time augmentation. x: (B, D) -> (B, 1)."""
        if self.training:
            x = apply_random_permutation_flat(x, severity=self.aug_severity, prob=AUG_APPLY_PROB)
        return self.head(self.net(x))


# ---------------------------------------------------------------------------
# E3: FlatMLPCanonEncoder — FlatMLP + L2 canonicalization (L-2-3)
# ---------------------------------------------------------------------------

class FlatMLPCanonEncoder(nn.Module):
    """FlatMLP with L2 normalization canonicalization pre-processing (E3).

    Normalizes each weight vector to unit L2 norm before MLP forward.
    Applied at both train and eval time.
    """

    def __init__(self, input_dim: int, hidden_dim: int = 512) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
        )
        self.head = nn.Linear(hidden_dim, 1)

        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.kaiming_uniform_(m.weight, nonlinearity="relu")
                if m.bias is not None:
                    nn.init.zeros_(m.bias)

    def forward(self, x: Tensor) -> Tensor:
        """Forward pass with L2 canonicalization. x: (B, D) -> (B, 1)."""
        x = l2_normalize_weights(x)
        return self.head(self.net(x))


# ---------------------------------------------------------------------------
# E4: NFTEquivariantEncoder (ported verbatim from H-E1 — L-2-1)
# ---------------------------------------------------------------------------

class NFTEquivariantEncoder(nn.Module):
    """NFT encoder with per-layer projections and equivariant self-attention (E4).

    Parameters
    ----------
    layer_fan_ins : list[int]
        Fan-in dimension for each weight layer.
    d_model : int
        Token embedding dimension (default 128).
    n_heads : int
        Number of attention heads (default 4).
    """

    def __init__(
        self,
        layer_fan_ins: list,
        d_model: int = 128,
        n_heads: int = 4,
    ) -> None:
        super().__init__()

        for fan_in in layer_fan_ins:
            if fan_in <= 0:
                raise ValueError(f"fan_in must be > 0, got {fan_in}")

        self.d_model = d_model
        self.layer_fan_ins = layer_fan_ins

        self.layer_projections = nn.ModuleList(
            [nn.Linear(fan_in, d_model) for fan_in in layer_fan_ins]
        )

        self.attn = nn.MultiheadAttention(d_model, n_heads, batch_first=True)
        self.norm = nn.LayerNorm(d_model)
        self.head = nn.Linear(d_model, 1)
        self.last_token_shape = None

        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.kaiming_uniform_(m.weight, nonlinearity="relu")
                if m.bias is not None:
                    nn.init.zeros_(m.bias)

    def forward(self, weight_matrices: list) -> Tensor:
        """Forward pass. weight_matrices: list[(B, n_units_l, fan_in_l)] -> (B, 1)."""
        token_seqs = []
        for l, W_l in enumerate(weight_matrices):
            tokens_l = self.layer_projections[l](W_l)
            token_seqs.append(tokens_l)

        all_tokens = torch.cat(token_seqs, dim=1)
        B, N, D = all_tokens.shape
        self.last_token_shape = (B, N, D)

        attn_out, _ = self.attn(all_tokens, all_tokens, all_tokens)
        attn_out = self.norm(attn_out + all_tokens)

        pooled = attn_out.mean(dim=1)
        return self.head(pooled)

    def get_last_token_shape(self):
        """Return (B, total_neurons, d_model) from last forward call."""
        return self.last_token_shape


# ---------------------------------------------------------------------------
# E5: NFTAugEncoder — NFT + augmentation (L-2-2)
# ---------------------------------------------------------------------------

class NFTAugEncoder(nn.Module):
    """NFT with random neuron permutation augmentation during training (E5).

    Augmentation applies at AUG_APPLY_PROB probability, severity=1.0.
    Disabled during eval mode.
    """

    def __init__(
        self,
        layer_fan_ins: list,
        d_model: int = 128,
        n_heads: int = 4,
    ) -> None:
        super().__init__()

        for fan_in in layer_fan_ins:
            if fan_in <= 0:
                raise ValueError(f"fan_in must be > 0, got {fan_in}")

        self.d_model = d_model
        self.layer_fan_ins = layer_fan_ins
        self.aug_severity = 1.0

        self.layer_projections = nn.ModuleList(
            [nn.Linear(fan_in, d_model) for fan_in in layer_fan_ins]
        )
        self.attn = nn.MultiheadAttention(d_model, n_heads, batch_first=True)
        self.norm = nn.LayerNorm(d_model)
        self.head = nn.Linear(d_model, 1)
        self.last_token_shape = None

        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.kaiming_uniform_(m.weight, nonlinearity="relu")
                if m.bias is not None:
                    nn.init.zeros_(m.bias)

    def forward(self, weight_matrices: list) -> Tensor:
        """Forward pass with training-time augmentation."""
        if self.training:
            weight_matrices = apply_random_permutation_nft(
                weight_matrices, severity=self.aug_severity, prob=AUG_APPLY_PROB
            )

        token_seqs = []
        for l, W_l in enumerate(weight_matrices):
            tokens_l = self.layer_projections[l](W_l)
            token_seqs.append(tokens_l)

        all_tokens = torch.cat(token_seqs, dim=1)
        B, N, D = all_tokens.shape
        self.last_token_shape = (B, N, D)

        attn_out, _ = self.attn(all_tokens, all_tokens, all_tokens)
        attn_out = self.norm(attn_out + all_tokens)

        pooled = attn_out.mean(dim=1)
        return self.head(pooled)

    def get_last_token_shape(self):
        return self.last_token_shape


# ---------------------------------------------------------------------------
# E6: OracleCanonEncoder — FlatMLP + oracle sort (L-2-3)
# ---------------------------------------------------------------------------

class OracleCanonEncoder(nn.Module):
    """FlatMLP with oracle sort canonicalization (E6).

    Sorts weight elements by descending value (deterministic canonical ordering).
    Applied at both train and eval time.
    """

    def __init__(self, input_dim: int, hidden_dim: int = 512) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
        )
        self.head = nn.Linear(hidden_dim, 1)

        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.kaiming_uniform_(m.weight, nonlinearity="relu")
                if m.bias is not None:
                    nn.init.zeros_(m.bias)

    def forward(self, x: Tensor) -> Tensor:
        """Forward pass with oracle sort canonicalization. x: (B, D) -> (B, 1)."""
        x = oracle_sort_weights(x)
        return self.head(self.net(x))


# ---------------------------------------------------------------------------
# Factory function (L-2-1, L-2-2, L-2-3)
# ---------------------------------------------------------------------------

def build_encoder(
    encoder_name: str,
    flat_input_dim: int,
    layer_fan_ins: list,
    hidden_dim: int = 512,
    d_model: int = 128,
    n_heads: int = 4,
) -> nn.Module:
    """Build encoder by name.

    Parameters
    ----------
    encoder_name : str
        One of ENCODER_NAMES: "flat-MLP", "flat-MLP+aug", "flat-MLP+canon",
        "NFT-base", "NFT+aug", "Oracle-canon".
    flat_input_dim : int
        Flattened weight dimension (for flat encoders).
    layer_fan_ins : list[int]
        Per-layer fan-in dimensions (for NFT encoders).
    hidden_dim : int
        Hidden dim for flat MLP encoders.
    d_model : int
        Token dimension for NFT encoders.
    n_heads : int
        Attention heads for NFT encoders.

    Returns
    -------
    nn.Module
        Encoder instance.

    Raises
    ------
    ValueError
        If encoder_name is not recognized.
    """
    if encoder_name == "flat-MLP":
        return FlatMLPEncoder(flat_input_dim, hidden_dim)
    elif encoder_name == "flat-MLP+aug":
        return FlatMLPAugEncoder(flat_input_dim, hidden_dim)
    elif encoder_name == "flat-MLP+canon":
        return FlatMLPCanonEncoder(flat_input_dim, hidden_dim)
    elif encoder_name == "NFT-base":
        return NFTEquivariantEncoder(layer_fan_ins, d_model, n_heads)
    elif encoder_name == "NFT+aug":
        return NFTAugEncoder(layer_fan_ins, d_model, n_heads)
    elif encoder_name == "Oracle-canon":
        return OracleCanonEncoder(flat_input_dim, hidden_dim)
    else:
        raise ValueError(
            f"Unknown encoder: '{encoder_name}'. "
            f"Valid options: flat-MLP, flat-MLP+aug, flat-MLP+canon, NFT-base, NFT+aug, Oracle-canon"
        )
