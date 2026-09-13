"""NPLinear, NFNEncoder, NFNWithHead, and grid search for H-M2 (Navon et al. 2023)."""
import logging
from typing import List, Tuple

import torch
import torch.nn as nn

logger = logging.getLogger("h-m2")


class NPLinear(nn.Module):
    """Permutation-equivariant linear layer (Navon et al. 2023).

    Maps list of per-layer tensors [B, n_elements_i, in_ch] → [B, n_elements_i, out_ch].
    Uses diag (per-element) + bias_terms (pooled invariant context) to preserve equivariance.
    """

    def __init__(self, in_ch: int, out_ch: int, weight_shapes: List[tuple]):
        super().__init__()
        self.weight_shapes = weight_shapes
        self.diag = nn.ModuleList([
            nn.Linear(in_ch, out_ch, bias=False) for _ in weight_shapes
        ])
        self.bias_terms = nn.ModuleList([
            nn.Linear(in_ch, out_ch, bias=True) for _ in weight_shapes
        ])

    def _n_elements(self, shape: tuple) -> int:
        n = 1
        for s in shape:
            n *= s
        return n

    def forward(self, Ws: List[torch.Tensor]) -> List[torch.Tensor]:
        """
        Args:
            Ws: list of L tensors, each [B, n_elements_i, in_ch]
        Returns:
            list of L tensors, each [B, n_elements_i, out_ch]
        """
        outputs = []
        for i, w in enumerate(Ws):
            # w: [B, n_i, in_ch]
            ctx = w.mean(dim=1, keepdim=True)           # [B, 1, in_ch]
            out = self.diag[i](w) + self.bias_terms[i](ctx).expand_as(self.diag[i](w))
            outputs.append(out)
        return outputs


class NFNEncoder(nn.Module):
    """NFN equivariant encoder: structured weight list → (B, embed_dim) embedding."""

    def __init__(
        self,
        weight_shapes: List[tuple],
        channel_dim: int,
        embed_dim: int = 128,
        n_layers: int = 3,
    ):
        super().__init__()
        self.weight_shapes = weight_shapes
        self.channel_dim = channel_dim
        self.embed_dim = embed_dim
        self.n_layers = n_layers
        self.act = nn.ReLU()
        self.in_proj = NPLinear(1, channel_dim, weight_shapes)
        self.layers = nn.ModuleList([
            NPLinear(channel_dim, channel_dim, weight_shapes)
            for _ in range(n_layers - 1)
        ])
        self.readout = nn.Linear(channel_dim, embed_dim)

    def _prepare_inputs(self, weights: List[torch.Tensor]) -> List[torch.Tensor]:
        """Reshape each raw weight tensor to [B, n_elements_i, 1]."""
        prepared = []
        for w in weights:
            B = w.shape[0]
            prepared.append(w.reshape(B, -1).unsqueeze(-1))  # [B, n_i, 1]
        return prepared

    def forward(self, weights: List[torch.Tensor]) -> torch.Tensor:
        """
        Args:
            weights: list of 8 tensors, each [B, *layer_shape]
        Returns:
            embedding: [B, embed_dim]
        """
        Ws = self._prepare_inputs(weights)          # list of [B, n_i, 1]
        Ws = [self.act(x) for x in self.in_proj(Ws)]   # list of [B, n_i, ch]
        for layer in self.layers:
            Ws = [self.act(x) for x in layer(Ws)]  # list of [B, n_i, ch]
        # Global mean pool: mean over n_i per layer, then mean over layers
        layer_means = torch.stack(
            [w.mean(dim=1) for w in Ws], dim=1
        )  # [B, n_layers_total, ch]
        pooled = layer_means.mean(dim=1)            # [B, ch]
        return self.readout(pooled)                 # [B, embed_dim]


class NFNWithHead(nn.Module):
    """NFN encoder + Linear(embed_dim, 1) accuracy prediction head."""

    def __init__(self, encoder: NFNEncoder, embed_dim: int = 128):
        super().__init__()
        self.encoder = encoder
        self.head = nn.Linear(embed_dim, 1)

    def forward(self, weights: List[torch.Tensor]) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Args:
            weights: list of 8 tensors, each [B, *layer_shape]
        Returns:
            embedding: [B, embed_dim], prediction: [B, 1]
        """
        embedding = self.encoder(weights)
        prediction = self.head(embedding)
        return embedding, prediction


def count_params(model: nn.Module) -> int:
    """Return total trainable parameter count."""
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def grid_search_nfn(
    weight_shapes: List[tuple],
    channel_dim_candidates: List[int],
    n_layers_candidates: List[int],
    embed_dim: int,
    target_min: int,
    target_max: int,
) -> Tuple[NFNEncoder, int, int, int]:
    """Grid search channel_dim x n_layers to hit [target_min, target_max] params.

    Returns: (encoder, channel_dim, n_layers, param_count)
    Raises ValueError if no config hits target range.
    """
    tried = []
    for channel_dim in channel_dim_candidates:
        for n_layers in n_layers_candidates:
            encoder = NFNEncoder(weight_shapes, channel_dim, embed_dim, n_layers)
            model = NFNWithHead(encoder, embed_dim)
            n_params = count_params(model)
            tried.append((channel_dim, n_layers, n_params))
            logger.info(
                f"[H-M2] Grid search: channel_dim={channel_dim}, n_layers={n_layers}, params={n_params:,}"
            )
            if target_min <= n_params <= target_max:
                logger.info(
                    f"[H-M2] Selected: channel_dim={channel_dim}, n_layers={n_layers}, params={n_params:,}"
                )
                return encoder, channel_dim, n_layers, n_params

    details = "\n".join(
        f"  channel_dim={cd}, n_layers={nl} → {p:,}" for cd, nl, p in tried
    )
    raise ValueError(
        f"No config fits [{target_min:,}, {target_max:,}] param budget.\n"
        f"Tried:\n{details}"
    )
