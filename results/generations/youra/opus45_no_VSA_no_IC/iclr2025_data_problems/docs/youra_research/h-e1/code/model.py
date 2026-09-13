"""ResNet-18 adapted for CIFAR-10."""

import torch.nn as nn
from torchvision.models import resnet18
import config


def build_model():
    """ResNet-18 modified for 32x32 CIFAR input."""
    model = resnet18(weights=None, num_classes=config.NUM_CLASSES)
    # Adapt for CIFAR: 3x3 conv, stride 1, no maxpool
    model.conv1 = nn.Conv2d(3, 64, kernel_size=3, stride=1, padding=1, bias=False)
    model.maxpool = nn.Identity()
    return model
