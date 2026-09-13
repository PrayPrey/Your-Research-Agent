"""Linear probe analysis module for H-M1."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "h-e1", "code"))

import torch
import torch.nn as nn
from model import build_resnet18


class LinearProbeAnalysis(nn.Module):
    def __init__(self, backbone: nn.Module, feature_dim: int = 512):
        super().__init__()
        self.backbone = backbone
        self.feature_dim = feature_dim

    def extract_features(self, x: torch.Tensor) -> torch.Tensor:
        with torch.no_grad():
            feats = self.backbone(x)
        return feats


def load_frozen_backbone(checkpoint_path: str, num_classes: int = 2, device: str = "cuda") -> nn.Module:
    model = build_resnet18(num_classes=num_classes, pretrained=False)
    state_dict = torch.load(checkpoint_path, map_location=device)
    model.load_state_dict(state_dict)
    model.fc = nn.Identity()
    model.eval()
    model.requires_grad_(False)
    return model.to(device)
