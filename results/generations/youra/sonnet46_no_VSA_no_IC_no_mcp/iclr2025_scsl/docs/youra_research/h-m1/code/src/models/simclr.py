import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.models as models


class ProjectionHead(nn.Module):
    def __init__(self, in_dim: int = 2048, hidden_dim: int = 2048, out_dim: int = 128):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden_dim),
            nn.ReLU(inplace=True),
            nn.Linear(hidden_dim, out_dim),
        )

    def forward(self, h: torch.Tensor) -> torch.Tensor:
        z = self.net(h)
        return F.normalize(z, dim=1)    # L2-normalized


class SimCLRModel(nn.Module):
    def __init__(self):
        super().__init__()
        backbone = models.resnet50(weights=None)
        backbone.fc = nn.Identity()     # Remove classification head; outputs 2048-dim
        self.backbone = backbone
        self.projection_head = ProjectionHead()

    def forward(self, x: torch.Tensor):
        h = self.backbone(x)            # (B, 2048)
        z = self.projection_head(h)     # (B, 128) L2-normalized
        return h, z

    def get_backbone(self) -> nn.Module:
        return self.backbone
