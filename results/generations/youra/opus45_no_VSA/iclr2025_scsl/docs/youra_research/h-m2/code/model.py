import torch
import torch.nn as nn
import torchvision.models as models
from torchvision.models import ResNet50_Weights

from config import CONFIG


def create_pretrained_model(seed: int) -> nn.Module:
    torch.manual_seed(seed)
    model = models.resnet50(weights=ResNet50_Weights.IMAGENET1K_V2)
    model.fc = nn.Linear(2048, CONFIG.num_classes)
    nn.init.xavier_uniform_(model.fc.weight)
    nn.init.zeros_(model.fc.bias)
    return model.double()
