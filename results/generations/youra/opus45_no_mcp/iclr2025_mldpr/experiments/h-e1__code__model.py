import torch.nn as nn
from torchvision import models


def build_resnet18(num_classes: int = 10) -> nn.Module:
    model = models.resnet18(weights=None)
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    return model
