"""
ResNet-18 with binary classification head for H-E1 experiment
"""

import torch
import torch.nn as nn
from torchvision import models


class ResNet18Binary(nn.Module):
    """ResNet-18 with binary classification head"""

    def __init__(self, pretrained: bool = True, num_classes: int = 2):
        """
        Initialize ResNet-18 with ImageNet pretrained weights.

        Args:
            pretrained: Load ImageNet pretrained weights
            num_classes: Output dimension (2 for binary classification)
        """
        super().__init__()
        self.num_classes = num_classes

        # Load pretrained ResNet-18
        self.resnet = models.resnet18(pretrained=pretrained)

        # Replace final FC layer for binary classification
        num_features = self.resnet.fc.in_features
        self.resnet.fc = nn.Linear(num_features, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.

        Args:
            x: Input images [B, 3, H, W]

        Returns:
            logits: Class logits [B, num_classes]
        """
        return self.resnet(x)


def get_model(method: str = "Joint", pretrained: bool = True) -> nn.Module:
    """
    Factory function to create model for specified method.

    Args:
        method: Training method (all use same ResNet-18)
        pretrained: Use ImageNet pretrained weights

    Returns:
        ResNet18Binary model
    """
    return ResNet18Binary(pretrained=pretrained, num_classes=2)
