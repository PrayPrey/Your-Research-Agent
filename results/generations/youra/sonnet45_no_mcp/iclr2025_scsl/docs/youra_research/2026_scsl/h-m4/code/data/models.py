"""Model definitions"""

import torch
import torch.nn as nn
from torchvision import models

def get_resnet50(num_classes: int = 2, pretrained: bool = True) -> nn.Module:
    """
    Get ResNet-50 model for Waterbirds.

    Args:
        num_classes: Number of output classes (2 for Waterbirds)
        pretrained: Whether to use ImageNet pretrained weights

    Returns:
        ResNet-50 model
    """
    if pretrained:
        model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
    else:
        model = models.resnet50(weights=None)

    # Replace final layer
    num_features = model.fc.in_features
    model.fc = nn.Linear(num_features, num_classes)

    return model
