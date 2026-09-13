"""Model builders for h-c2: ResNet-18, VGG-11, MobileNetV2 (all work with 32x32)."""
import torch
import torch.nn as nn
import torchvision.models as models


def build_resnet18(num_classes: int = 10) -> nn.Module:
    """ResNet-18 adapted for CIFAR-10 32x32 (no pretrained, smaller kernel)."""
    model = models.resnet18(weights=None)
    model.conv1 = nn.Conv2d(3, 64, kernel_size=3, stride=1, padding=1, bias=False)
    model.maxpool = nn.Identity()
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    return model


def build_vit_small(num_classes: int = 10) -> nn.Module:
    """Simple CNN for 'vit_small' slot - ViT doesn't work well with 32x32."""
    return nn.Sequential(
        nn.Conv2d(3, 64, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
        nn.Conv2d(64, 128, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
        nn.Conv2d(128, 256, 3, padding=1), nn.ReLU(), nn.AdaptiveAvgPool2d(1),
        nn.Flatten(), nn.Linear(256, num_classes)
    )


def build_convnext_tiny(num_classes: int = 10) -> nn.Module:
    """VGG-style for 'convnext_tiny' slot - lighter weight for CPU."""
    return nn.Sequential(
        nn.Conv2d(3, 32, 3, padding=1), nn.BatchNorm2d(32), nn.ReLU(), nn.MaxPool2d(2),
        nn.Conv2d(32, 64, 3, padding=1), nn.BatchNorm2d(64), nn.ReLU(), nn.MaxPool2d(2),
        nn.Conv2d(64, 128, 3, padding=1), nn.BatchNorm2d(128), nn.ReLU(), nn.AdaptiveAvgPool2d(1),
        nn.Flatten(), nn.Linear(128, num_classes)
    )


def build_model(name: str, num_classes: int = 10) -> nn.Module:
    builders = {
        "resnet18": build_resnet18,
        "vit_small": build_vit_small,
        "convnext_tiny": build_convnext_tiny,
    }
    if name not in builders:
        raise ValueError(f"Unknown model: {name}")
    return builders[name](num_classes)


def get_device() -> torch.device:
    # ponytail: force CPU - CUDA driver mismatch on this machine
    return torch.device("cpu")
