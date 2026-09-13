"""DeepSets Channel Encoder (C2) — permutation-invariant by construction."""
import torch
import torch.nn as nn
from data_loader import CONV_WEIGHT_KEYS, LAYER_WEIGHT_DIMS


class DeepSetsChannelEncoder(nn.Module):
    """
    Doubly-invariant DeepSets encoder for coupled S_n³ permutations.

    For each conv layer, apply phi to each individual weight scalar element (kH*kW kernel),
    then sum over BOTH C_out (rows) and C_in (columns) dimensions independently.
    This achieves invariance to both row and column channel permutations.

    Architecture per layer:
      W: (C_out, C_in, kH, kW)
      phi: R^{kH*kW} -> R^{hidden_dim}  (applied per (C_out, C_in) kernel)
      sum over C_in (inner): (C_out, hidden_dim)
      sum over C_out (outer): (hidden_dim,)  -- invariant to both row & col perms
      rho: R^{hidden_dim} -> R^{layer_embed_dim}

    OrbitVar = 0 by nested application of Deep Sets Theorem 2.
    """
    def __init__(
        self,
        kernel_dims: list = None,   # [kH*kW per conv layer] = [25, 25, 4]
        hidden_dim: int = 64,
        embed_dim: int = 128,
    ):
        super().__init__()
        # kernel sizes: conv1=5x5=25, conv2=5x5=25, conv3=2x2=4
        if kernel_dims is None:
            kernel_dims = [25, 25, 4]
        n_layers = len(kernel_dims)
        layer_embed_dim = embed_dim // n_layers  # 128//3 = 42

        # phi: maps each kernel (kH*kW) → hidden_dim
        self.phi_layers = nn.ModuleList([
            nn.Sequential(nn.Linear(kd, hidden_dim), nn.ReLU())
            for kd in kernel_dims
        ])
        self.rho_layers = nn.ModuleList([
            nn.Sequential(nn.Linear(hidden_dim, layer_embed_dim), nn.ReLU())
            for _ in kernel_dims
        ])
        # ponytail: proj absorbs embed_dim // n_layers rounding (42*3=126 != 128)
        self.proj = nn.Linear(layer_embed_dim * n_layers, embed_dim)
        self.conv_weight_keys = CONV_WEIGHT_KEYS

    def forward(self, state_dict: dict) -> torch.Tensor:
        """state_dict -> (embed_dim,) embedding invariant to coupled channel permutations."""
        layer_embeds = []
        for i, key in enumerate(self.conv_weight_keys):
            W = state_dict[key]              # (C_out, C_in, kH, kW)
            C_out, C_in, kH, kW = W.shape
            # Reshape to (C_out * C_in, kH*kW) — each kernel as one element
            W_kernels = W.reshape(C_out * C_in, kH * kW)   # (C_out*C_in, kernel_dim)
            phi_out = self.phi_layers[i](W_kernels)          # (C_out*C_in, hidden_dim)
            # Sum over all (C_out, C_in) pairs — invariant to both row AND col permutations
            # because sum({phi(w_{ij})}) = sum({phi(w_{sigma(i), tau(j)})}) for any sigma, tau
            sum_out = phi_out.sum(dim=0)                     # (hidden_dim,)
            rho_out = self.rho_layers[i](sum_out)            # (layer_embed_dim,)
            layer_embeds.append(rho_out)

        cat = torch.cat(layer_embeds, dim=0)                 # (layer_embed_dim * n_layers,)
        return self.proj(cat)                                 # (embed_dim,)


def build_c2_encoder(embed_dim: int = 128, hidden_dim: int = 64) -> DeepSetsChannelEncoder:
    return DeepSetsChannelEncoder(
        kernel_dims=[25, 25, 4],  # kH*kW per conv layer
        hidden_dim=hidden_dim,
        embed_dim=embed_dim,
    )
