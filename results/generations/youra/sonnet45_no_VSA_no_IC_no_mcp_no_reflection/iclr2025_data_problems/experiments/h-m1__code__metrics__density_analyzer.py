"""Information Density Analyzer: Entropy + Fisher Information"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch import Tensor
from typing import Tuple


class InformationDensityAnalyzer(nn.Module):
    """Wrap GPT-2 with density tracking."""

    def __init__(self, model: nn.Module, vocab_size: int):
        super().__init__()
        self.model = model
        self.vocab_size = vocab_size

    def compute_entropy(self, logits: Tensor) -> float:
        """Shannon entropy from logits. logits: [B, L, V] -> scalar"""
        with torch.no_grad():
            probs = F.softmax(logits, dim=-1)  # [B, L, V]
            log_probs = F.log_softmax(logits, dim=-1)
            entropy = -(probs * log_probs).sum(dim=-1).mean().item()
        return entropy

    def compute_fisher_trace(self) -> float:
        """Diagonal FIM trace. Returns: sum(grad^2)"""
        fisher_trace = sum(
            (p.grad ** 2).sum().item()
            for p in self.model.parameters()
            if p.grad is not None
        )
        return fisher_trace

    def forward(
        self,
        input_ids: Tensor,
        labels: Tensor
    ) -> Tuple[Tensor, float, float]:
        """Forward + backward + metrics.

        Args:
            input_ids: [B, L]
            labels: [B, L]

        Returns:
            loss: scalar tensor
            entropy: float (bits/token)
            fisher_trace: float
        """
        # Standard forward
        outputs = self.model(input_ids, labels=labels)
        loss = outputs.loss

        # Entropy (before backward)
        entropy = self.compute_entropy(outputs.logits)

        # Backward
        loss.backward()

        # Fisher trace (after backward)
        fisher_trace = self.compute_fisher_trace()

        return loss, entropy, fisher_trace
