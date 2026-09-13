"""
GradCAM Temporal Ratio Tracker for h-e3.
Tracks R_temporal(t) = A_spurious / (A_spurious + A_core) across training epochs.
"""

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from captum.attr import LayerGradCam
import numpy as np


class GradCAMTemporalTracker:
    """Tracks GradCAM attribution ratio over training epochs."""

    def __init__(self, model: nn.Module, target_layer: nn.Module, device: str = 'cuda'):
        """
        Initialize with model and target layer.

        Args:
            model: PyTorch model
            target_layer: Layer to compute GradCAM on (e.g., ResNet layer4)
            device: Computation device
        """
        self.model = model
        self.gradcam = LayerGradCam(model, target_layer)
        self.device = device
        self.R_history = {}  # {epoch: R_temporal}

    def compute_epoch_ratio(
        self,
        dataloader: DataLoader,
        dataset_name: str,
        max_batches: int = 100
    ) -> float:
        """
        Compute R_temporal = A_spurious / (A_spurious + A_core) for current epoch.

        Args:
            dataloader: Validation set loader
            dataset_name: Dataset name for mask creation
            max_batches: Number of batches to sample for efficiency

        Returns:
            R_temporal: Temporal ratio (scalar in [0, 1])
        """
        from region_masks import create_spurious_mask, create_core_mask

        self.model.eval()
        ratios = []

        with torch.no_grad():
            for batch_idx, batch in enumerate(dataloader):
                if batch_idx >= max_batches:
                    break

                # Unpack batch (handle WILDS format)
                if len(batch) == 3:
                    images, labels, metadata = batch
                else:
                    images, labels = batch

                images = images.to(self.device)
                labels = labels.to(self.device).long()

                # Compute GradCAM attributions
                attributions = self.gradcam.attribute(images, target=labels)  # [B, 1, H, W]
                attributions = torch.abs(attributions).squeeze(1)  # [B, H, W]

                # Get region masks (downsampled to match attributions)
                attr_shape = attributions.shape[-2:]  # (H, W)
                spurious_mask = create_spurious_mask(images, dataset_name, target_size=attr_shape)
                core_mask = create_core_mask(images, dataset_name, target_size=attr_shape)

                # Compute regional attributions
                A_spurious = (attributions * spurious_mask).sum(dim=(1, 2))  # [B]
                A_core = (attributions * core_mask).sum(dim=(1, 2))  # [B]

                # Temporal ratio per sample
                R_batch = A_spurious / (A_spurious + A_core + 1e-8)
                ratios.extend(R_batch.cpu().tolist())

        # Aggregate across all samples
        R_temporal = np.mean(ratios)
        return float(R_temporal)

    def record_epoch(self, epoch: int, ratio: float):
        """Store R_temporal for epoch."""
        self.R_history[epoch] = ratio

    def get_history(self):
        """Returns {epoch: R_temporal} mapping."""
        return self.R_history
