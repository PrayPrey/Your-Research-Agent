import torch
from torch import nn
import torchvision.models as models

def build_resnet50(num_classes: int = 2) -> nn.Module:
    model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
    model.fc = nn.Linear(2048, num_classes)
    return model
