import torch.nn as nn
from torchvision import models

def build_resnet50(num_classes: int = 2, pretrained: bool = True) -> nn.Module:
    weights = models.ResNet50_Weights.IMAGENET1K_V1 if pretrained else None
    model = models.resnet50(weights=weights)
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    return model
