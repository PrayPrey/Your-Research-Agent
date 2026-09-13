"""Model and OnsetDelayTracker implementation."""
import numpy as np
import torch
import torch.nn as nn
from torchvision import models


def build_resnet18(num_classes: int = 2, pretrained: bool = True) -> nn.Module:
    """Build ResNet-18 with replaced final layer."""
    weights = models.ResNet18_Weights.IMAGENET1K_V1 if pretrained else None
    model = models.resnet18(weights=weights)
    model.fc = nn.Linear(512, num_classes)
    return model


class OnsetDelayTracker:
    """Track per-sample loss and compute onset delay d_i.

    Two detection modes:
    1. Relative threshold: d_i = first epoch where L_i(t) < threshold * L_i(0)
    2. Loss-at-T: Predict minority as samples with high loss at epoch T_early
    """

    def __init__(self, n_samples: int, n_epochs: int, threshold: float = 0.9):
        self.n_samples = n_samples
        self.n_epochs = n_epochs
        self.threshold = threshold
        self.loss_matrix = np.full((n_samples, n_epochs), np.nan)

    def update(self, epoch: int, sample_indices: np.ndarray, losses: np.ndarray) -> None:
        """Update loss matrix for given samples at given epoch."""
        self.loss_matrix[sample_indices, epoch] = losses

    def get_onset_delays(self) -> np.ndarray:
        """Compute onset delay d_i for each sample using relative threshold."""
        L0 = self.loss_matrix[:, 0]
        target = self.threshold * L0

        d_i = np.full(self.n_samples, -1, dtype=np.int32)

        for i in range(self.n_samples):
            if np.isnan(L0[i]):
                continue
            for t in range(1, self.n_epochs):
                if np.isnan(self.loss_matrix[i, t]):
                    break
                if self.loss_matrix[i, t] < target[i]:
                    d_i[i] = t
                    break

        return d_i

    def get_loss_at_epoch(self, epoch: int) -> np.ndarray:
        """Get loss values at a specific epoch."""
        return self.loss_matrix[:, epoch].copy()

    def predict_minority(self, T_early: int = 20) -> np.ndarray:
        """Predict minority using loss-at-T approach.

        Samples with loss > median loss at T_early are predicted as minority.
        """
        loss_at_T = self.get_loss_at_epoch(min(T_early, self.n_epochs - 1))
        valid_mask = ~np.isnan(loss_at_T)

        threshold_loss = np.percentile(loss_at_T[valid_mask], 95)

        pred = np.zeros(self.n_samples, dtype=bool)
        pred[valid_mask] = loss_at_T[valid_mask] > threshold_loss
        return pred

    def get_loss_history(self) -> np.ndarray:
        """Return the full loss matrix."""
        return self.loss_matrix
