"""
Gradient variance and forgetting event trackers for h-e2.
"""

import torch
import torch.nn as nn
import numpy as np


class GradientVarianceTracker:
    """Track gradient norms with rolling window variance."""

    def __init__(self, window_size: int = 3):
        self.window_size = window_size
        self.grad_history = []  # list of float (epoch grad norms)

    def log_gradient_norm(self, model: nn.Module) -> float:
        """Compute L2 norm of all gradients. Returns scalar."""
        total = sum(p.grad.norm(2).item() ** 2 for p in model.parameters() if p.grad is not None)
        norm = total ** 0.5
        self.grad_history.append(norm)
        return norm

    def compute_variance(self) -> float:
        """Rolling variance over last window_size epochs."""
        if len(self.grad_history) < self.window_size:
            return 0.0
        window = self.grad_history[-self.window_size:]
        return float(np.var(window))

    def get_all_variances(self, checkpoint_epochs: list[int]) -> list[float]:
        """Compute variance at specific checkpoints."""
        variances = []
        for epoch in checkpoint_epochs:
            if epoch <= len(self.grad_history):
                end_idx = epoch
                start_idx = max(0, end_idx - self.window_size)
                window = self.grad_history[start_idx:end_idx]
                if len(window) >= 2:
                    variances.append(float(np.var(window)))
                else:
                    variances.append(0.0)
            else:
                variances.append(0.0)
        return variances


class ForgettingTracker:
    """Track per-sample predictions across epochs."""

    def __init__(self, num_samples: int):
        self.num_samples = num_samples
        self.predictions = {}  # {epoch: [N] tensor}
        self.labels = None  # [N] ground truth

    def log_predictions(self, epoch: int, preds: torch.Tensor, labels: torch.Tensor):
        """Store predictions. preds: [N], labels: [N]"""
        self.predictions[epoch] = preds.cpu()
        if self.labels is None:
            self.labels = labels.cpu()

    def compute_forgetting_events(self) -> float:
        """Count correct->incorrect flips. Returns: mean events per sample."""
        if len(self.predictions) < 2:
            return 0.0

        forgetting_count = torch.zeros(self.num_samples)
        epochs = sorted(self.predictions.keys())

        for i in range(len(epochs) - 1):
            curr_correct = (self.predictions[epochs[i]] == self.labels)
            next_correct = (self.predictions[epochs[i+1]] == self.labels)
            forgetting_count += (curr_correct & ~next_correct).float()

        return forgetting_count.mean().item()
