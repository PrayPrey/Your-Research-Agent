"""Model definitions for h-e1 experiment.

FlatMLPEncoder: 3-layer ReLU MLP for flattened weight vectors.
NFTEquivariantEncoder: NFT encoder with per-layer projections and equivariant attention.
"""
import logging
import torch
import torch.nn as nn
from torch import Tensor

logger = logging.getLogger(__name__)


class FlatMLPEncoder(nn.Module):
    """3-hidden-layer ReLU MLP for flattened weight vectors.

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

        # Kaiming init
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.kaiming_uniform_(m.weight, nonlinearity="relu")
                if m.bias is not None:
                    nn.init.zeros_(m.bias)

    def forward(self, x: Tensor) -> Tensor:
        """Forward pass.

        Parameters
        ----------
        x : Tensor
            Shape (B, input_dim).

        Returns
        -------
        Tensor
            Shape (B, 1).
        """
        return self.head(self.net(x))


class NFTEquivariantEncoder(nn.Module):
    """NFT encoder with per-layer projections and equivariant self-attention.

    Parameters
    ----------
    layer_fan_ins : list[int]
        Fan-in dimension for each weight layer after reshape to (n_units, fan_in).
    d_model : int
        Token embedding dimension (default 128).
    n_heads : int
        Number of attention heads (default 4).

    Raises
    ------
    ValueError
        If any fan_in <= 0.
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

        # Per-layer projection: maps fan_in -> d_model for each layer
        self.layer_projections = nn.ModuleList(
            [nn.Linear(fan_in, d_model) for fan_in in layer_fan_ins]
        )

        # Equivariant self-attention
        self.attn = nn.MultiheadAttention(d_model, n_heads, batch_first=True)
        self.norm = nn.LayerNorm(d_model)
        self.head = nn.Linear(d_model, 1)

        self.last_token_shape = None

        # Kaiming init for projections and head
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.kaiming_uniform_(m.weight, nonlinearity="relu")
                if m.bias is not None:
                    nn.init.zeros_(m.bias)

    def forward(self, weight_matrices: list) -> Tensor:
        """Forward pass.

        Parameters
        ----------
        weight_matrices : list[Tensor]
            List of tensors, each shape (B, n_units_l, fan_in_l).

        Returns
        -------
        Tensor
            Shape (B, 1).
        """
        token_seqs = []
        for l, W_l in enumerate(weight_matrices):
            # W_l: (B, n_units_l, fan_in_l)
            tokens_l = self.layer_projections[l](W_l)  # (B, n_units_l, d_model)
            token_seqs.append(tokens_l)

        all_tokens = torch.cat(token_seqs, dim=1)  # (B, total_units, d_model)
        B, N, D = all_tokens.shape
        self.last_token_shape = (B, N, D)
        logger.info(f"NFT tokens: (B={B}, N_neurons={N}, d_model={D})")

        attn_out, _ = self.attn(all_tokens, all_tokens, all_tokens)  # (B, N, d_model)
        attn_out = self.norm(attn_out + all_tokens)  # residual + LayerNorm

        pooled = attn_out.mean(dim=1)  # (B, d_model)
        return self.head(pooled)  # (B, 1)

    def get_last_token_shape(self):
        """Return (B, total_neurons, d_model) from last forward call."""
        return self.last_token_shape
