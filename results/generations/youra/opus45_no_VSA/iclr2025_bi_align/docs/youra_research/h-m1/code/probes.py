"""Adversarial Prober: BAI head + reward head with GRL."""
import torch
import torch.nn as nn
from grl import GradientReversalLayer


class AdversarialProber(nn.Module):
    def __init__(self, hidden_dim: int):
        super().__init__()
        self.bai_probe = nn.Linear(hidden_dim, 1)
        self.grl = GradientReversalLayer(alpha=0.0)
        self.reward_probe = nn.Linear(hidden_dim, 1)

    def forward(self, h):
        bai_logits = self.bai_probe(h).squeeze(-1)
        reward_logits = self.reward_probe(self.grl(h)).squeeze(-1)
        return bai_logits, reward_logits

    def set_alpha(self, alpha: float):
        self.grl.set_alpha(alpha)


class BaselineRewardProbe(nn.Module):
    """Non-adversarial reward probe for R² baseline comparison."""
    def __init__(self, hidden_dim: int):
        super().__init__()
        self.probe = nn.Linear(hidden_dim, 1)

    def forward(self, h):
        return self.probe(h).squeeze(-1)
