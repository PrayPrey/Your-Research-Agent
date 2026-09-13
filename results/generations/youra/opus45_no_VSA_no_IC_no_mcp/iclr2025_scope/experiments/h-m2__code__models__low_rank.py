import torch
import torch.nn as nn
from torch import Tensor


class LowRankProjection(nn.Module):
    """Low-rank projection for task-conditioned modulation (LoRA-style)."""

    def __init__(self, task_emb_dim: int, target_dim: int, rank: int = 32):
        super().__init__()
        self.down = nn.Linear(task_emb_dim, rank, bias=False)
        self.up = nn.Linear(rank, target_dim, bias=False)

        nn.init.normal_(self.down.weight, std=0.1)
        nn.init.normal_(self.up.weight, std=0.1)

    def forward(self, task_embedding: Tensor) -> Tensor:
        return self.up(self.down(task_embedding))
