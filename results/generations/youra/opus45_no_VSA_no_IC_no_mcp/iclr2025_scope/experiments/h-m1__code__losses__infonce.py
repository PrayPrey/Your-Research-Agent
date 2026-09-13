import torch
import torch.nn as nn
import torch.nn.functional as F
from torch import Tensor


class InfoNCELoss(nn.Module):
    """InfoNCE contrastive loss on cluster labels."""

    def __init__(self, temperature: float = 0.1):
        super().__init__()
        self.temperature = temperature

    def forward(self, embeddings: Tensor, cluster_labels: Tensor) -> Tensor:
        """embeddings: [B, D], cluster_labels: [B] int64"""
        embeddings = F.normalize(embeddings, dim=-1)

        sim_matrix = embeddings @ embeddings.T / self.temperature

        batch_size = embeddings.shape[0]
        mask = torch.eye(batch_size, dtype=torch.bool, device=embeddings.device)
        sim_matrix = sim_matrix.masked_fill(mask, float("-inf"))

        labels_i = cluster_labels.unsqueeze(1)
        labels_j = cluster_labels.unsqueeze(0)
        pos_mask = (labels_i == labels_j) & ~mask

        valid_rows = pos_mask.any(dim=1)
        if not valid_rows.any():
            return torch.tensor(0.0, device=embeddings.device, requires_grad=True)

        log_prob = F.log_softmax(sim_matrix, dim=1)

        pos_log_prob = log_prob.masked_fill(~pos_mask, 0.0)
        pos_counts = pos_mask.sum(dim=1).clamp(min=1)
        loss_per_sample = -pos_log_prob.sum(dim=1) / pos_counts

        loss = loss_per_sample[valid_rows].mean()
        return loss
