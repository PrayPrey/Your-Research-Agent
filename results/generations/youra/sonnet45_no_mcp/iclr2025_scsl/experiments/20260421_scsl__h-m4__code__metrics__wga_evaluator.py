"""Worst-Group Accuracy (WGA) evaluator"""

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from typing import List
import numpy as np

class WGAEvaluator:
    """Worst-group accuracy evaluator"""

    def __init__(
        self,
        model: nn.Module,
        dataloader: DataLoader,
        num_groups: int = 4,
        device: str = "cuda"
    ):
        """
        Args:
            model: ResNet-50 model
            dataloader: Waterbirds test loader with group labels
            num_groups: Number of groups (4 for Waterbirds)
            device: Computation device
        """
        self.model = model
        self.dataloader = dataloader
        self.num_groups = num_groups
        self.device = device

    def evaluate(self) -> float:
        """
        Compute WGA = min(group_accuracies).

        Algorithm:
        1. For each group g in [0, 1, 2, 3]:
        2.   Compute accuracy_g on samples where group_label == g
        3. Return min(accuracy_0, accuracy_1, accuracy_2, accuracy_3)

        Returns:
            wga: Float in [0, 1]
        """
        group_accs = self._compute_group_accuracies()
        return min(group_accs)

    def _compute_group_accuracies(self) -> List[float]:
        """
        Compute per-group accuracy.

        Returns:
            List[float] of length num_groups (4)
        """
        group_correct = [0] * self.num_groups
        group_total = [0] * self.num_groups

        self.model.eval()
        with torch.no_grad():
            for batch in self.dataloader:
                # Handle different batch formats
                if len(batch) == 3:
                    images, labels, groups = batch
                else:
                    # If groups not provided, skip
                    continue

                images = images.to(self.device)
                labels = labels.to(self.device)

                outputs = self.model(images)
                preds = outputs.argmax(dim=1)

                for g in range(self.num_groups):
                    mask = (groups == g)
                    if mask.sum() > 0:
                        group_correct[g] += (preds[mask] == labels[mask]).sum().item()
                        group_total[g] += mask.sum().item()

        # Compute accuracies (handle division by zero)
        group_accuracies = []
        for g in range(self.num_groups):
            if group_total[g] > 0:
                group_accuracies.append(group_correct[g] / group_total[g])
            else:
                group_accuracies.append(0.0)

        return group_accuracies

    def get_group_accuracies(self) -> List[float]:
        """Get all group accuracies (for visualization)"""
        return self._compute_group_accuracies()
