"""Model builder for h-m1."""
import torch
import torch.nn as nn
import torchvision.models as models


def build_resnet18_cifar10(pretrained: bool = True) -> nn.Module:
    """ResNet-18 with fc layer replaced for CIFAR-10 (10 classes)."""
    weights = models.ResNet18_Weights.IMAGENET1K_V1 if pretrained else None
    model = models.resnet18(weights=weights)
    model.fc = nn.Linear(model.fc.in_features, 10)
    return model


def get_device() -> torch.device:
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")
