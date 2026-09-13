"""ResNet-50 baseline model."""
import torch
import torch.nn as nn
import torchvision.models as models


def build_resnet50(num_classes: int = 2) -> nn.Module:
    model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
    model.fc = nn.Linear(2048, num_classes)
    return model


def get_flat_grad(model: nn.Module) -> torch.Tensor:
    grads = []
    for p in model.parameters():
        if p.grad is not None:
            grads.append(p.grad.view(-1))
    return torch.cat(grads)
