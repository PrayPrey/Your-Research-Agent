"""MINE estimator for H-M1 experiment."""
import torch
import torch.nn as nn
import torch.nn.functional as F


class MINEEstimator(nn.Module):
    """Mutual Information Neural Estimation using Donsker-Varadhan bound."""

    def __init__(self, feedback_dim: int = 256, code_dim: int = 256, hidden_dim: int = 512):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(feedback_dim + code_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1),
        )
        self.ema_weight = 0.01
        self.running_mean = None

    def forward(self, feedback_emb: torch.Tensor, code_emb: torch.Tensor) -> torch.Tensor:
        joint = torch.cat([feedback_emb, code_emb], dim=-1)
        return self.network(joint)

    def estimate_mi(
        self,
        feedback_emb: torch.Tensor,
        code_emb: torch.Tensor,
        marginal_code_emb: torch.Tensor = None,
    ) -> torch.Tensor:
        """Estimate I(E;F) using Donsker-Varadhan lower bound with EMA bias correction."""
        joint_scores = self.forward(feedback_emb, code_emb)

        if marginal_code_emb is None:
            perm = torch.randperm(code_emb.size(0), device=code_emb.device)
            marginal_code_emb = code_emb[perm]

        marginal_scores = self.forward(feedback_emb, marginal_code_emb)

        # EMA bias correction
        exp_marginal = torch.exp(marginal_scores).mean()
        if self.running_mean is None:
            self.running_mean = exp_marginal.detach()
        else:
            self.running_mean = (
                (1 - self.ema_weight) * self.running_mean + self.ema_weight * exp_marginal.detach()
            )

        mi_lb = joint_scores.mean() - torch.log(self.running_mean + 1e-8)
        return mi_lb


def train_mine(
    estimator: MINEEstimator,
    feedback_emb: torch.Tensor,
    code_emb: torch.Tensor,
    lr: float = 0.001,
    batch_size: int = 128,
    n_iters: int = 5000,
) -> tuple[MINEEstimator, list[float]]:
    """Train MINE estimator."""
    device = feedback_emb.device
    estimator = estimator.to(device)
    optimizer = torch.optim.Adam(estimator.parameters(), lr=lr)

    n_samples = feedback_emb.size(0)
    losses = []

    for i in range(n_iters):
        idx = torch.randint(0, n_samples, (batch_size,), device=device)
        fb_batch = feedback_emb[idx]
        cd_batch = code_emb[idx]

        # Negative MI as loss (maximize MI = minimize -MI)
        mi = estimator.estimate_mi(fb_batch, cd_batch)
        loss = -mi

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        losses.append(mi.item())

        if (i + 1) % 1000 == 0:
            print(f"  MINE iter {i+1}/{n_iters}, MI estimate: {mi.item():.4f}")

    return estimator, losses
