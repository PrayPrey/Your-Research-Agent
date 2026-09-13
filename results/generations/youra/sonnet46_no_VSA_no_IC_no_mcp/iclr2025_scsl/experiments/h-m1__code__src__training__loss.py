import torch
import torch.nn as nn
import torch.nn.functional as F


class NTXentLoss(nn.Module):
    """NT-Xent (Normalized Temperature-scaled Cross Entropy) loss for SimCLR."""

    def __init__(self, temperature: float = 0.5):
        super().__init__()
        self.temperature = temperature

    def forward(self, z1: torch.Tensor, z2: torch.Tensor) -> torch.Tensor:
        """
        z1, z2: (B, D) L2-normalized projection vectors
        """
        B = z1.shape[0]
        z = torch.cat([z1, z2], dim=0)                          # (2B, D)
        sim = torch.mm(z, z.t()) / self.temperature             # (2B, 2B) cosine similarities

        # Mask self-similarity (diagonal)
        mask = torch.eye(2 * B, dtype=torch.bool, device=z.device)
        sim.masked_fill_(mask, float('-inf'))

        # Positive pair labels: z1[i] pairs with z2[i] at position i+B, and vice versa
        labels = torch.cat([
            torch.arange(B, 2 * B, device=z.device),
            torch.arange(B, device=z.device),
        ])
        return F.cross_entropy(sim, labels)
