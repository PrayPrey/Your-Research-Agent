"""CISE Channel-Index Sinusoidal Encoder (C1) — NOT permutation-invariant (baseline contrast)."""
import math
import torch
import torch.nn as nn


class CISEEncoder(nn.Module):
    """
    Channel-Index Sinusoidal Encoder.
    Uses fixed sinusoidal positional encoding indexed by output channel position.
    Explicitly NOT permutation-invariant: channel index is preserved via PE.
    No sort/argsort/topk anywhere in this implementation.
    """

    def __init__(self, embed_dim: int = 64, max_channels: int = 16):
        super().__init__()
        self.embed_dim = embed_dim
        self.max_channels = max_channels
        pe = self._build_pe_table(max_channels, embed_dim)
        self.register_buffer('pe', pe)  # (max_channels, embed_dim)
        self.proj = nn.Linear(embed_dim, embed_dim)

    @staticmethod
    def _build_pe_table(max_channels: int, embed_dim: int) -> torch.Tensor:
        """Standard sinusoidal PE. Returns (max_channels, embed_dim)."""
        pe = torch.zeros(max_channels, embed_dim)
        pos = torch.arange(max_channels, dtype=torch.float).unsqueeze(1)  # (C, 1)
        div = torch.exp(
            torch.arange(0, embed_dim, 2, dtype=torch.float)
            * (-math.log(10000.0) / embed_dim)
        )  # (embed_dim/2,)
        pe[:, 0::2] = torch.sin(pos * div)
        half = embed_dim // 2
        pe[:, 1::2] = torch.cos(pos * div[:half])
        return pe

    def forward(self, state_dict: dict) -> torch.Tensor:
        """
        state_dict -> (embed_dim,) float32 embedding.
        For each conv layer, accumulate weight-scaled PE vectors over output channels.
        NOT invariant: channel index position preserved via PE lookup.
        """
        accum = torch.zeros(self.embed_dim, device=self.pe.device)
        for key, W in state_dict.items():
            if not isinstance(W, torch.Tensor) or W.dim() != 4:
                continue  # skip non-conv weights
            C_out = W.shape[0]
            n_channels = min(C_out, self.max_channels)
            for c in range(n_channels):
                w_mean = W[c].abs().mean()  # scalar
                accum = accum + w_mean * self.pe[c]  # (embed_dim,)
        return self.proj(accum)  # (embed_dim,)


def build_c1_encoder(embed_dim: int = 64) -> CISEEncoder:
    return CISEEncoder(embed_dim=embed_dim, max_channels=16)
