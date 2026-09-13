"""SequentialPEBaseline: replicates SANE's sequential [n, l, k] position encoding.

Used ONLY for timing comparison — not for accuracy prediction.
SANE uses a learned embedding table indexed by sequential position [n, l, k].
For fair comparison with OrbitPEComputer, this baseline also uses nn.Embedding
lookups (one per position dimension) and projects to token_dim, matching the
computational structure of SANE's actual implementation.
"""
import torch
import torch.nn as nn
from torch import Tensor
from typing import Dict

_MAX_SEQ_LEN = 4096  # Maximum global sequence positions


class SequentialPEBaseline(nn.Module):
    """Replicates SANE's sequential [n, l, k] positional encoding.

    For each weight parameter, returns a (cout, token_dim) tensor where
    each row encodes the sequential position of that output channel token.

    Uses learned embeddings (matching SANE architecture) for fair timing comparison.
    """

    def __init__(self, token_dim: int):
        super().__init__()
        self.token_dim = token_dim
        # SANE uses separate learned embeddings for each position dimension
        self.n_embed = nn.Embedding(_MAX_SEQ_LEN, token_dim)  # global position
        self.l_embed = nn.Embedding(256, token_dim)            # layer index
        self.k_embed = nn.Embedding(_MAX_SEQ_LEN, token_dim)  # within-layer position

    def forward(self, state_dict: Dict[str, Tensor]) -> Dict[str, Tensor]:
        """Replicate SANE sequential [n, l, k] position encoding via embedding lookup.

        Returns dict: param_name -> (cout, token_dim) PE tensor.
          n = global position index (cumulative row count across layers)
          l = layer index (0-indexed)
          k = within-layer position (row index, 0-indexed per layer)
        """
        pe_dict: Dict[str, Tensor] = {}
        global_n = 0
        for layer_idx, (param_name, weight) in enumerate(state_dict.items()):
            if not param_name.endswith(".weight"):
                continue
            if weight.dim() < 2:
                continue

            cout = weight.shape[0]
            device = weight.device

            # Build position indices
            n_idx = torch.arange(global_n, global_n + cout, device=device).clamp(0, _MAX_SEQ_LEN - 1)
            l_idx = torch.full((cout,), layer_idx, dtype=torch.long, device=device).clamp(0, 255)
            k_idx = torch.arange(cout, device=device).clamp(0, _MAX_SEQ_LEN - 1)

            with torch.no_grad():
                # Sum of three position embeddings (standard additive PE pattern)
                pe = self.n_embed(n_idx) + self.l_embed(l_idx) + self.k_embed(k_idx)

            pe_dict[param_name] = pe
            global_n += cout

        return pe_dict


def compute_sequential_pe_all(
    state_dict: Dict[str, Tensor],
    baseline: "SequentialPEBaseline",
) -> Dict[str, Tensor]:
    """Convenience wrapper for SequentialPEBaseline.forward().

    Returns pe_vectors dict: param_name -> (cout, token_dim).
    """
    return baseline.forward(state_dict)
