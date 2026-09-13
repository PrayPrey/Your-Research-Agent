"""ResNet-50 ERM model with penultimate-layer access."""
import os
import torch
import torch.nn as nn
from torch import Tensor
import torchvision.models as tv_models
from typing import Optional


class ERMModel(nn.Module):
    def __init__(self, num_classes: int = 2, pretrained: bool = True):
        super().__init__()
        weights = tv_models.ResNet50_Weights.IMAGENET1K_V1 if pretrained else None
        backbone = tv_models.resnet50(weights=weights)
        # features = everything except the final FC layer
        self.features = nn.Sequential(*list(backbone.children())[:-1])
        feat_dim = backbone.fc.in_features  # 2048
        self.classifier = nn.Linear(feat_dim, num_classes)

    def forward(self, x: Tensor) -> Tensor:
        feat = self.features(x)            # (B, 2048, 1, 1)
        feat = feat.squeeze(-1).squeeze(-1)  # (B, 2048)
        return self.classifier(feat)

    def get_feature_extractor(self) -> nn.Sequential:
        return self.features


def get_model(num_classes: int = 2, pretrained: bool = True) -> ERMModel:
    return ERMModel(num_classes=num_classes, pretrained=pretrained)


def save_checkpoint(model: ERMModel, optimizer, epoch: int, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    torch.save({
        'epoch': epoch,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
    }, path)


def load_checkpoint(model: ERMModel, path: str, device: torch.device) -> int:
    ckpt = torch.load(path, map_location=device)
    model.load_state_dict(ckpt['model_state_dict'])
    return ckpt.get('epoch', 0)
