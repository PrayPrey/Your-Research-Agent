"""MLP model architectures for variance measurement."""

import torch
import torch.nn as nn
import torch.nn.functional as F


class SimpleMLP1Layer(nn.Module):
    """1-layer MLP: 784 -> 128 (ReLU) -> 10

    Architecture:
        Input: 28x28 images (flattened to 784)
        Hidden: 128 units with ReLU activation
        Output: 10 classes
        Parameters: ~196K
    """

    def __init__(self, input_size: int = 784, hidden_size: int = 128, output_size: int = 10):
        super().__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, output_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass.

        Args:
            x: Input tensor [B, 1, 28, 28]

        Returns:
            Output logits [B, 10]
        """
        x = x.view(x.size(0), -1)  # Flatten: [B, 1, 28, 28] -> [B, 784]
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x


class SimpleMLP2Layer(nn.Module):
    """2-layer MLP: 784 -> 256 (ReLU) -> 128 (ReLU) -> 10

    Architecture:
        Input: 28x28 images (flattened to 784)
        Hidden1: 256 units with ReLU activation
        Hidden2: 128 units with ReLU activation
        Output: 10 classes
        Parameters: ~400K
    """

    def __init__(
        self,
        input_size: int = 784,
        hidden1: int = 256,
        hidden2: int = 128,
        output_size: int = 10
    ):
        super().__init__()
        self.fc1 = nn.Linear(input_size, hidden1)
        self.fc2 = nn.Linear(hidden1, hidden2)
        self.fc3 = nn.Linear(hidden2, output_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass.

        Args:
            x: Input tensor [B, 1, 28, 28]

        Returns:
            Output logits [B, 10]
        """
        x = x.view(x.size(0), -1)  # Flatten: [B, 1, 28, 28] -> [B, 784]
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x


def create_model(architecture: str) -> nn.Module:
    """Factory function for creating models.

    Args:
        architecture: '1layer' or '2layer'

    Returns:
        Model instance

    Raises:
        ValueError: If architecture is unknown
    """
    if architecture == "1layer":
        return SimpleMLP1Layer()
    elif architecture == "2layer":
        return SimpleMLP2Layer()
    else:
        raise ValueError(f"Unknown architecture: {architecture}")
