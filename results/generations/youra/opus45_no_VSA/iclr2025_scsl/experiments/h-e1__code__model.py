import torch
import torch.nn as nn
import torchvision.models as models


def create_random_model(seed: int) -> nn.Module:
    torch.manual_seed(seed)
    model = models.resnet50(weights=None)
    model.fc = nn.Linear(2048, 2)
    return model.double()
