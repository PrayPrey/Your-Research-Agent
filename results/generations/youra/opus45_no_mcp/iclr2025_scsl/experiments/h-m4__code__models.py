"""H-M4 Models: ResNet-50 for all benchmarks"""
import torch
import torch.nn as nn
from torchvision import models


def build_resnet50(num_classes: int, image_size: int = 224) -> nn.Module:
    """ImageNet-pretrained ResNet50 with adapted head."""
    model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
    model.fc = nn.Linear(model.fc.in_features, num_classes)

    if image_size == 32:
        model.conv1 = nn.Conv2d(3, 64, kernel_size=3, stride=1, padding=1, bias=False)
        model.maxpool = nn.Identity()

    return model
