"""ResNet-50 model wrapper with feature extraction."""
import torch
import torch.nn as nn
from torchvision import models


class FeatureResNet50(nn.Module):
    """ResNet-50 with classification head and feature extraction capability."""

    def __init__(self, num_classes: int, pretrained: bool = True):
        super().__init__()
        weights = models.ResNet50_Weights.IMAGENET1K_V1 if pretrained else None
        self.backbone = models.resnet50(weights=weights)
        self.backbone.fc = nn.Linear(2048, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass returning classification logits."""
        return self.backbone(x)

    def extract_features(self, x: torch.Tensor) -> torch.Tensor:
        """Extract 2048-d avgpool features."""
        model = self.backbone
        x = model.conv1(x)
        x = model.bn1(x)
        x = model.relu(x)
        x = model.maxpool(x)
        x = model.layer1(x)
        x = model.layer2(x)
        x = model.layer3(x)
        x = model.layer4(x)
        x = model.avgpool(x)
        x = torch.flatten(x, 1)
        return x
