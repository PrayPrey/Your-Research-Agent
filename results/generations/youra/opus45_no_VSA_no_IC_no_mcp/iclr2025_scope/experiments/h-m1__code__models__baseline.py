import torch
import torch.nn as nn
from torch import Tensor


class RandomEmbeddingBaseline(nn.Module):
    """Frozen random embedding baseline."""

    def __init__(self, embedding_dim: int, num_tasks: int = 8, seed: int = 42):
        super().__init__()
        g = torch.Generator().manual_seed(seed)
        self.embeddings = nn.Parameter(
            torch.randn(num_tasks, embedding_dim, generator=g),
            requires_grad=False
        )
        self.num_tasks = num_tasks
        self.embedding_dim = embedding_dim

    def forward(self, hidden_states: Tensor, task_ids: Tensor = None) -> Tensor:
        """Returns random embeddings based on task_ids or random selection."""
        batch_size = hidden_states.shape[0]
        if task_ids is not None:
            return self.embeddings[task_ids]
        idx = torch.randint(0, self.num_tasks, (batch_size,))
        return self.embeddings[idx]
