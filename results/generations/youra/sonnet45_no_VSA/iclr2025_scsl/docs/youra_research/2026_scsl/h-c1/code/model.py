"""Model architecture module for MNIST classification."""
import torch
import torch.nn as nn
import torch.nn.functional as F
from config import MODEL_CONFIG


class StandardCNN(nn.Module):
    """Standard CNN for MNIST (PyTorch Official pattern)."""

    def __init__(self):
        """Initialize 2-conv + 2-FC architecture."""
        super(StandardCNN, self).__init__()

        # Conv layers
        self.conv1 = nn.Conv2d(1, MODEL_CONFIG["conv1_out_channels"], kernel_size=3, stride=1)
        self.conv2 = nn.Conv2d(MODEL_CONFIG["conv1_out_channels"], MODEL_CONFIG["conv2_out_channels"], kernel_size=3, stride=1)

        # Dropout layers
        self.dropout1 = nn.Dropout2d(MODEL_CONFIG["dropout1"])
        self.dropout2 = nn.Dropout(MODEL_CONFIG["dropout2"])

        # FC layers
        self.fc1 = nn.Linear(9216, MODEL_CONFIG["fc1_out_features"])
        self.fc2 = nn.Linear(MODEL_CONFIG["fc1_out_features"], MODEL_CONFIG["num_classes"])

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass.

        Args:
            x: Input images [B, 1, 28, 28]

        Returns:
            Log probabilities [B, 10]
        """
        # Conv block 1: [B, 1, 28, 28] -> [B, 32, 26, 26]
        x = F.relu(self.conv1(x))

        # Conv block 2: [B, 32, 26, 26] -> [B, 64, 24, 24]
        x = F.relu(self.conv2(x))

        # MaxPool: [B, 64, 24, 24] -> [B, 64, 12, 12]
        x = F.max_pool2d(x, 2)

        # Dropout: [B, 64, 12, 12]
        x = self.dropout1(x)

        # Flatten: [B, 64, 12, 12] -> [B, 9216]
        x = torch.flatten(x, 1)

        # FC1: [B, 9216] -> [B, 128]
        x = self.fc1(x)
        x = F.relu(x)

        # Dropout: [B, 128]
        x = self.dropout2(x)

        # FC2: [B, 128] -> [B, 10]
        x = self.fc2(x)

        # Log softmax: [B, 10]
        return F.log_softmax(x, dim=1)
