"""ResNet-50 model wrapper for Waterbirds binary classification."""

import torch
import torch.nn as nn
import torchvision.models as models


def get_resnet50(num_classes: int = 2, pretrained: bool = True) -> nn.Module:
    """
    Load ResNet-50 with modified final layer.

    Args:
        num_classes: Number of output classes (2 for Waterbirds)
        pretrained: Load ImageNet pretrained weights

    Returns:
        ResNet-50 model
    """
    model = models.resnet50(pretrained=pretrained)

    # Modify final layer for binary classification
    in_features = model.fc.in_features
    model.fc = nn.Linear(in_features, num_classes)

    return model
