import torch
import torch.nn as nn
from torch import Tensor


class TaskEmbeddingEncoder(nn.Module):
    """Projects pooled hidden states into task embedding space."""

    def __init__(self, hidden_dim: int, embedding_dim: int, num_tasks: int = 8):
        super().__init__()
        self.projection = nn.Linear(hidden_dim, embedding_dim)
        self.num_tasks = num_tasks

    def forward(self, hidden_states: Tensor) -> Tensor:
        """hidden_states: [B, seq, hidden_dim] -> [B, embedding_dim]"""
        projected = self.projection(hidden_states)
        pooled = projected.mean(dim=1)
        return pooled
