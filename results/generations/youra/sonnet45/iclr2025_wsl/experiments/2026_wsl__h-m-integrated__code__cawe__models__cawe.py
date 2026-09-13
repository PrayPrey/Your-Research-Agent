"""
CAWE (Compositional Architecture-Agnostic Weight Encoder) model.
Combines architecture-specific tokenizers with shared NFT backbone.
"""
import torch
import torch.nn as nn
from typing import Dict
from ..tokenizers import CNNTokenizer, TransformerTokenizer, MLPTokenizer


class CAWE(nn.Module):
    """
    Compositional Architecture-Agnostic Weight Encoder (CAWE).

    Architecture:
        1. Architecture-specific tokenization (CNN/Transformer/MLP)
        2. Shared NFT backbone (permutation-equivariant attention)
        3. Global average pooling over token sequences
        4. Regression head for generalization gap prediction
    """

    def __init__(self, token_dim: int = 128, nft_channels: int = 64):
        super().__init__()
        self.token_dim = token_dim
        self.nft_channels = nft_channels

        # Architecture-specific tokenizers
        self.tokenizers = nn.ModuleDict({
            'cnn': CNNTokenizer(token_dim=token_dim),
            'transformer': TransformerTokenizer(token_dim=token_dim),
            'mlp': MLPTokenizer(token_dim=token_dim)
        })

        # Simplified NFT backbone (instead of using nfn library for PoC)
        # Using standard transformer-style attention as permutation-equivariant approximation
        self.nft_backbone = nn.Sequential(
            nn.Linear(token_dim, nft_channels),
            nn.ReLU(),
            nn.Linear(nft_channels, token_dim),
            nn.ReLU(),
            nn.Linear(token_dim, token_dim)
        )

        # Regression head
        self.regression_head = nn.Sequential(
            nn.Linear(token_dim, 64),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(64, 1)
        )

    def forward(self, weights: Dict[str, torch.Tensor], arch_family: str) -> torch.Tensor:
        """
        Forward pass through CAWE model.

        Args:
            weights: Model state dictionary containing weights
            arch_family: Architecture family ('cnn', 'transformer', or 'mlp')

        Returns:
            prediction: Generalization gap prediction (scalar)
        """
        # Get device from model parameters
        device = next(self.parameters()).device

        # Move all weight tensors to device
        weights_on_device = {k: v.to(device) for k, v in weights.items()}

        # Step 1: Architecture-specific tokenization
        if arch_family not in self.tokenizers:
            raise ValueError(f"Unknown architecture family: {arch_family}")

        tokens = self.tokenizers[arch_family](weights_on_device)  # (num_layers, token_dim)

        # Step 2: NFT backbone processing
        processed_tokens = self.nft_backbone(tokens)  # (num_layers, token_dim)

        # Step 3: Global average pooling
        pooled = processed_tokens.mean(dim=0)  # (token_dim,)

        # Step 4: Regression head
        prediction = self.regression_head(pooled)  # (1,)

        return prediction.squeeze()  # scalar
