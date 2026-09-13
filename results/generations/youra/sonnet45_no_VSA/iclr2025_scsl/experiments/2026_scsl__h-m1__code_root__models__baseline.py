"""Standard CNN for MNIST (PyTorch official example architecture)"""
import sys
from pathlib import Path
import torch
import torch.nn as nn
import torch.nn.functional as F

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import ModelConfig


class StandardCNN(nn.Module):
    """Standard CNN from PyTorch MNIST official example"""

    def __init__(self, config: ModelConfig):
        super().__init__()
        # Conv1: 1 → 32 channels, kernel 3×3
        self.conv1 = nn.Conv2d(config.in_channels, 32, kernel_size=3)
        # Conv2: 32 → 64 channels, kernel 3×3
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3)
        # MaxPool: 2×2
        self.pool = nn.MaxPool2d(2, 2)
        # Dropout2d after pooling
        self.dropout_conv = nn.Dropout2d(p=config.dropout_conv)
        # Flatten: 64×12×12 → 9216 (after conv1, conv2, pool)
        self.fc1 = nn.Linear(64 * 12 * 12, 128)
        # Dropout before final layer
        self.dropout_fc = nn.Dropout(p=config.dropout_fc)
        # Output: 128 → 10
        self.fc2 = nn.Linear(128, config.num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.

        Args:
            x: [B, 1, 28, 28]

        Returns:
            logits: [B, 10]
        """
        # Conv1: [B, 1, 28, 28] → [B, 32, 26, 26]
        x = F.relu(self.conv1(x))
        # Conv2: [B, 32, 26, 26] → [B, 64, 24, 24]
        x = F.relu(self.conv2(x))
        # Pool: [B, 64, 24, 24] → [B, 64, 12, 12]
        x = self.pool(x)
        # Dropout conv
        x = self.dropout_conv(x)
        # Flatten: [B, 64, 12, 12] → [B, 9216]
        x = torch.flatten(x, 1)
        # FC1: [B, 9216] → [B, 128]
        x = F.relu(self.fc1(x))
        # Dropout FC
        x = self.dropout_fc(x)
        # FC2: [B, 128] → [B, 10]
        x = self.fc2(x)
        return F.log_softmax(x, dim=1)
