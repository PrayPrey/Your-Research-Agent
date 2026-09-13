"""FlatMLPEncoder, FlatMLPWithHead, and grid search for H-M1."""
import logging
from typing import List, Tuple

import torch
import torch.nn as nn

logger = logging.getLogger("h-m1")


class FlatMLPEncoder(nn.Module):
    """Flat MLP encoder: concatenated weight vector → embedding."""

    def __init__(self, input_dim: int, hidden_dims: List[int], embed_dim: int = 128, dropout: float = 0.1):
        super().__init__()
        layers = []
        in_d = input_dim
        for h in hidden_dims:
            layers += [nn.Linear(in_d, h), nn.ReLU(), nn.Dropout(dropout)]
            in_d = h
        layers.append(nn.Linear(in_d, embed_dim))
        self.net = nn.Sequential(*layers)
        self.embed_dim = embed_dim
        self.input_dim = input_dim
        self.hidden_dims = hidden_dims

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Input: (B, input_dim) → Output: (B, embed_dim)
        return self.net(x)


class FlatMLPWithHead(nn.Module):
    """Encoder + linear prediction head for accuracy regression."""

    def __init__(self, encoder: FlatMLPEncoder, embed_dim: int = 128):
        super().__init__()
        self.encoder = encoder
        self.head = nn.Linear(embed_dim, 1)

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        # Returns (embedding (B, embed_dim), prediction (B, 1))
        embedding = self.encoder(x)
        prediction = self.head(embedding)
        return embedding, prediction


def count_params(model: nn.Module) -> int:
    """Count total trainable parameters."""
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def grid_search_architecture(
    input_dim: int,
    candidates: List[List[int]],
    embed_dim: int,
    dropout: float,
    target_min: int,
    target_max: int,
) -> Tuple[FlatMLPEncoder, List[int], int]:
    """Iterate candidates; return first encoder within param budget [target_min, target_max]."""
    tried = []
    for hidden_dims in candidates:
        encoder = FlatMLPEncoder(input_dim, hidden_dims, embed_dim, dropout)
        n_params = count_params(encoder)
        tried.append((hidden_dims, n_params))
        logger.info(f"[H-M1] Grid search: hidden_dims={hidden_dims}, params={n_params:,}")
        if target_min <= n_params <= target_max:
            logger.info(f"[H-M1] Selected hidden_dims={hidden_dims}, params={n_params:,}")
            return encoder, hidden_dims, n_params

    # No candidate fits — report all tried
    details = ", ".join(f"{hd}→{p:,}" for hd, p in tried)
    raise ValueError(
        f"No candidate fits [{target_min:,}, {target_max:,}] param budget. Tried: {details}"
    )
