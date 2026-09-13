"""
Operation-Specific Encoders (Task A-2)
SANE-inspired conv encoder, UNF-inspired attention encoder, MLP encoder
"""

from typing import List, Optional
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch import Tensor


class SANEConvEncoder(nn.Module):
    """Convolutional weight encoder with spatial tokenization (SANE-inspired)"""

    def __init__(self, d_out: int = 256, d_token: int = 64, dropout: float = 0.1):
        """
        Args:
            d_out: Output embedding dimension
            d_token: Token dimension for spatial tokenization
            dropout: Dropout rate
        """
        super().__init__()
        self.d_out = d_out
        self.d_token = d_token

        # Spatial tokenization: project flattened weights
        self.token_proj = nn.Linear(1, d_token)

        # Token aggregation
        self.token_aggregator = nn.Sequential(
            nn.Linear(d_token, d_token),
            nn.ReLU(),
            nn.Dropout(dropout)
        )

        # Final projection to output dimension
        self.output_proj = nn.Linear(d_token, d_out)

    def spatial_tokenize(self, weight: Tensor) -> Tensor:
        """
        Tokenize convolution kernel spatially.

        Args:
            weight: [C_out, C_in, K, K] convolution weight
        Returns:
            tokens: [N_tokens, d_token] spatial tokens
        """
        # Flatten spatial dimensions and channel input
        # [C_out, C_in, K, K] -> [C_out * C_in * K * K]
        flat_weight = weight.reshape(-1)

        # Project each weight value to token space
        # [N] -> [N, 1] -> [N, d_token]
        tokens = self.token_proj(flat_weight.unsqueeze(-1))

        return tokens

    def forward(self, conv_weights: List[Tensor]) -> Tensor:
        """
        Encode convolutional weights.

        Args:
            conv_weights: List of [C_out, C_in, K, K] tensors (variable per layer)
        Returns:
            embedding: [d_out] single embedding for all conv layers
        """
        if len(conv_weights) == 0:
            # Return zero embedding if no conv layers
            return torch.zeros(self.d_out, device=next(self.parameters()).device)

        layer_embeddings = []

        for weight in conv_weights:
            # Spatial tokenization
            tokens = self.spatial_tokenize(weight)  # [N_tokens, d_token]

            # Aggregate tokens (mean pooling across tokens)
            layer_embed = tokens.mean(dim=0)  # [d_token]

            # Apply aggregator
            layer_embed = self.token_aggregator(layer_embed)  # [d_token]

            layer_embeddings.append(layer_embed)

        # Mean pool across layers
        stacked = torch.stack(layer_embeddings, dim=0)  # [L, d_token]
        pooled = stacked.mean(dim=0)  # [d_token]

        # Project to output dimension
        output = self.output_proj(pooled)  # [d_out]

        return output


class UNFAttentionEncoder(nn.Module):
    """Attention weight encoder with permutation equivariance (UNF-inspired)"""

    def __init__(self, d_out: int = 256, d_hidden: int = 128, dropout: float = 0.1):
        """
        Args:
            d_out: Output embedding dimension
            d_hidden: Hidden dimension for processing
            dropout: Dropout rate
        """
        super().__init__()
        self.d_out = d_out
        self.d_hidden = d_hidden

        # Equivariant processing: use statistics that are permutation-invariant
        # Row/column statistics: 4 values per dimension (mean, std, min, max)
        self.feature_proj = nn.Sequential(
            nn.Linear(4, d_hidden),
            nn.ReLU(),
            nn.Dropout(dropout)
        )

        # Output projection
        self.output_proj = nn.Linear(d_hidden, d_out)

    def equivariant_process(self, weight: Tensor) -> Tensor:
        """
        Apply permutation-equivariant processing via statistics.

        Args:
            weight: [N_heads, D, D] attention weight matrix
        Returns:
            features: [N_heads, d_hidden] per-head features
        """
        N_heads, D, _ = weight.shape

        # Extract row and column statistics (permutation-invariant)
        row_mean = weight.mean(dim=-1)  # [N_heads, D]
        row_std = weight.std(dim=-1)    # [N_heads, D]
        col_mean = weight.mean(dim=-2)  # [N_heads, D]
        col_std = weight.std(dim=-2)    # [N_heads, D]

        # Stack statistics: [N_heads, D, 4]
        stats = torch.stack([row_mean, row_std, col_mean, col_std], dim=-1)

        # Pool across D dimension: [N_heads, 4]
        stats_pooled = stats.mean(dim=1)

        # Project to hidden dimension
        features = self.feature_proj(stats_pooled)  # [N_heads, d_hidden]

        return features

    def forward(self, attn_weights: List[Tensor]) -> Tensor:
        """
        Encode attention weights.

        Args:
            attn_weights: List of [N_heads, D, D] or [N_heads, D_qk, D_v] tensors
        Returns:
            embedding: [d_out] single embedding for all attention layers
        """
        if len(attn_weights) == 0:
            return torch.zeros(self.d_out, device=next(self.parameters()).device)

        layer_embeddings = []

        for weight in attn_weights:
            # Ensure square matrices (pad if needed for Q-K-V)
            if weight.shape[-2] != weight.shape[-1]:
                # Pad to square
                D_max = max(weight.shape[-2], weight.shape[-1])
                padded = torch.zeros(
                    weight.shape[0], D_max, D_max,
                    device=weight.device, dtype=weight.dtype
                )
                padded[:, :weight.shape[-2], :weight.shape[-1]] = weight
                weight = padded

            # Equivariant processing
            head_features = self.equivariant_process(weight)  # [N_heads, d_hidden]

            # Mean pool across heads
            layer_embed = head_features.mean(dim=0)  # [d_hidden]

            layer_embeddings.append(layer_embed)

        # Mean pool across layers
        stacked = torch.stack(layer_embeddings, dim=0)  # [L, d_hidden]
        pooled = stacked.mean(dim=0)  # [d_hidden]

        # Project to output dimension
        output = self.output_proj(pooled)  # [d_out]

        return output


class MLPEncoder(nn.Module):
    """MLP weight encoder using DeepSets-style aggregation"""

    def __init__(self, d_out: int = 256, d_hidden: int = 128, dropout: float = 0.1):
        """
        Args:
            d_out: Output embedding dimension
            d_hidden: Hidden dimension
            dropout: Dropout rate
        """
        super().__init__()
        self.d_out = d_out
        self.d_hidden = d_hidden

        # Embed weight matrix statistics
        self.matrix_embedder = nn.Sequential(
            nn.Linear(3, d_hidden),  # 3 statistics: norm, mean, std
            nn.ReLU(),
            nn.Dropout(dropout)
        )

        # Output projection
        self.output_proj = nn.Linear(d_hidden, d_out)

    def embed_weight_matrix(self, weight: Tensor) -> Tensor:
        """
        Embed single weight matrix using statistics.

        Args:
            weight: [D_out, D_in] FC layer weight
        Returns:
            embedding: [d_hidden]
        """
        # Compute statistics
        norm = torch.norm(weight).unsqueeze(0)  # [1]
        mean = weight.mean().unsqueeze(0)       # [1]
        std = weight.std().unsqueeze(0)         # [1]

        stats = torch.cat([norm, mean, std], dim=0)  # [3]

        # Embed
        embedding = self.matrix_embedder(stats)  # [d_hidden]

        return embedding

    def forward(self, mlp_weights: List[Tensor]) -> Tensor:
        """
        Encode MLP/FC layer weights.

        Args:
            mlp_weights: List of [D_out, D_in] tensors
        Returns:
            embedding: [d_out] single embedding for all MLP layers
        """
        if len(mlp_weights) == 0:
            return torch.zeros(self.d_out, device=next(self.parameters()).device)

        layer_embeddings = []

        for weight in mlp_weights:
            # Embed weight matrix
            layer_embed = self.embed_weight_matrix(weight)  # [d_hidden]
            layer_embeddings.append(layer_embed)

        # Mean pool across layers (DeepSets aggregation)
        stacked = torch.stack(layer_embeddings, dim=0)  # [L, d_hidden]
        pooled = stacked.mean(dim=0)  # [d_hidden]

        # Project to output dimension
        output = self.output_proj(pooled)  # [d_out]

        return output
