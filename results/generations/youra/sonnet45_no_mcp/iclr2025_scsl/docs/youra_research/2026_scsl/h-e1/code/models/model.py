"""
Model architecture for H-E1
ResNet-50 with pretrained weights
"""

import torch
import torch.nn as nn
from torchvision import models


def get_resnet50(num_classes=2, pretrained=True):
    """
    Load ResNet-50 model with modified final layer.

    Args:
        num_classes: Number of output classes
        pretrained: Whether to use ImageNet pretrained weights

    Returns:
        ResNet-50 model
    """
    model = models.resnet50(pretrained=pretrained)

    # Replace final FC layer
    in_features = model.fc.in_features
    model.fc = nn.Linear(in_features, num_classes)

    return model


class GroupDROLoss(nn.Module):
    """
    Group-DRO loss: reweights groups to minimize worst-group loss.

    Reference: Sagawa et al. 2020 - Distributionally Robust Neural Networks
    """

    def __init__(self, num_groups=4, step_size=0.01):
        super().__init__()
        self.num_groups = num_groups
        self.step_size = step_size

        # Initialize group weights uniformly
        self.register_buffer('group_weights', torch.ones(num_groups) / num_groups)

    def forward(self, logits, labels, groups):
        """
        Compute Group-DRO loss.

        Args:
            logits: (B, C) model predictions
            labels: (B,) true labels
            groups: (B,) group indices

        Returns:
            loss: scalar tensor
        """
        # Compute per-sample loss
        criterion = nn.CrossEntropyLoss(reduction='none')
        losses = criterion(logits, labels)

        # Compute per-group loss
        group_losses = torch.zeros(self.num_groups, device=logits.device)
        group_counts = torch.zeros(self.num_groups, device=logits.device)

        for g in range(self.num_groups):
            mask = (groups == g)
            if mask.sum() > 0:
                group_losses[g] = losses[mask].mean()
                group_counts[g] = mask.sum().float()

        # Update group weights (exponential moving average)
        with torch.no_grad():
            self.group_weights = self.group_weights * torch.exp(self.step_size * group_losses)
            self.group_weights = self.group_weights / self.group_weights.sum()

        # Compute weighted loss
        loss = (group_losses * self.group_weights).sum()

        return loss
