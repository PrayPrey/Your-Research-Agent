"""
SNE Baseline Implementation (Task A-5)
DeepSets-style permutation-invariant encoder for comparison
"""

import torch
import torch.nn as nn
from torch import Tensor
from typing import List, Dict


class SNEBaseline(nn.Module):
    """SNE baseline using DeepSets-style permutation-invariant encoding"""

    def __init__(self, d_model: int = 256, dropout: float = 0.1):
        """
        Args:
            d_model: Embedding dimension
            dropout: Dropout rate
        """
        super().__init__()
        self.d_model = d_model

        # Per-element encoder: map weight statistics to embedding space
        self.element_encoder = nn.Sequential(
            nn.Linear(3, 128),  # 3 statistics: norm, mean, std
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(128, d_model)
        )

        # Aggregation is mean pooling (DeepSets)

    def embed_weight(self, weight: Tensor) -> Tensor:
        """
        Embed single weight tensor using statistics.

        Args:
            weight: [*] arbitrary shape weight tensor
        Returns:
            embedding: [d_model]
        """
        # Flatten weight
        flat = weight.reshape(-1)

        # Compute statistics
        norm = torch.norm(flat).unsqueeze(0)
        mean = flat.mean().unsqueeze(0)
        std = flat.std().unsqueeze(0)

        stats = torch.cat([norm, mean, std], dim=0)  # [3]

        # Encode
        embedding = self.element_encoder(stats)  # [d_model]

        return embedding

    def forward(
        self,
        model_weights: Dict[str, List[Tensor]],
        arch_graph=None  # Ignored for baseline
    ) -> Tensor:
        """
        Encode model weights using permutation-invariant aggregation.

        Args:
            model_weights: {"conv": [tensors], "attention": [tensors], "mlp": [tensors]}
            arch_graph: Ignored (for compatibility with CAPE interface)
        Returns:
            z_final: [d_model] final embedding
        """
        # Collect all weights
        all_weights = []
        for op_type in ["conv", "attention", "mlp"]:
            all_weights.extend(model_weights.get(op_type, []))

        if len(all_weights) == 0:
            device = next(self.parameters()).device
            return torch.zeros(self.d_model, device=device)

        # Embed each weight tensor
        embeddings = []
        for weight in all_weights:
            emb = self.embed_weight(weight)
            embeddings.append(emb)

        # Mean pooling (DeepSets aggregation)
        stacked = torch.stack(embeddings, dim=0)  # [L, d_model]
        z_final = stacked.mean(dim=0)  # [d_model]

        return z_final
