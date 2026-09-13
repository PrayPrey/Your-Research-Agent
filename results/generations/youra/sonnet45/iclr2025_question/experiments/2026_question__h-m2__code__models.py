"""Model architectures for H-M2."""

import torch
import torch.nn as nn


class MLP1Layer(nn.Module):
    """1-layer MLP: 784 → 128 → 10."""

    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(784, 128)
        self.fc2 = nn.Linear(128, 10)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = x.view(x.size(0), -1)  # Flatten
        x = self.relu(self.fc1(x))
        x = self.fc2(x)
        return x


class MLP2Layer(nn.Module):
    """2-layer MLP: 784 → 256 → 128 → 10."""

    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(784, 256)
        self.fc2 = nn.Linear(256, 128)
        self.fc3 = nn.Linear(128, 10)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = x.view(x.size(0), -1)  # Flatten
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.fc3(x)
        return x


def get_model(architecture: str) -> nn.Module:
    """Get model by architecture name."""
    if architecture == "1layer":
        return MLP1Layer()
    elif architecture == "2layer":
        return MLP2Layer()
    else:
        raise ValueError(f"Unknown architecture: {architecture}")


def get_flattened_params(model: nn.Module) -> torch.Tensor:
    """Extract flattened parameter vector from model."""
    params = []
    for param in model.parameters():
        params.append(param.data.view(-1))
    return torch.cat(params)


def count_parameters(model: nn.Module) -> int:
    """Count total trainable parameters."""
    return sum(p.numel() for p in model.parameters())
