"""Model definition module for H-E1 experiment.

Implements ResNet-50 classifier with pretrained ImageNet weights.
"""

import torch
import torch.nn as nn
import torchvision.models as models

from config import Config


class ResNet50Classifier(nn.Module):
    """ResNet-50 classifier for binary classification.

    Uses pretrained ImageNet weights with replaced final FC layer.
    """

    def __init__(self, num_classes: int = 2, pretrained: bool = True):
        """Initialize ResNet-50 classifier.

        Args:
            num_classes: Number of output classes (default: 2 for waterbird/landbird)
            pretrained: Whether to use ImageNet pretrained weights
        """
        super().__init__()

        # Load pretrained ResNet-50
        if pretrained:
            weights = models.ResNet50_Weights.IMAGENET1K_V1
            self.backbone = models.resnet50(weights=weights)
        else:
            self.backbone = models.resnet50(weights=None)

        # Replace final FC layer for binary classification
        in_features = self.backbone.fc.in_features
        self.backbone.fc = nn.Linear(in_features, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass.

        Args:
            x: Input images, shape (B, 3, 224, 224)

        Returns:
            Logits, shape (B, num_classes)
        """
        return self.backbone(x)


def build_model(config: Config) -> ResNet50Classifier:
    """Build model from configuration.

    Args:
        config: Experiment configuration

    Returns:
        Initialized ResNet50Classifier
    """
    model = ResNet50Classifier(
        num_classes=config.num_classes,
        pretrained=True,
    )
    return model
