"""SimpleMLP model architecture."""

from typing import List
import torch
import torch.nn as nn


MODEL_CONFIG = {
    "architecture": "SimpleMLP",
    "input_dim": 2352,
    "hidden_dims": [392, 256, 256],
    "num_classes": 10,
    "activation": "relu",
    "use_batch_norm": False,
    "use_residual": False,
    "initialization": "xavier_uniform"
}


class SimpleMLP(nn.Module):
    """Simple MLP without batch normalization or residual connections."""

    def __init__(
        self,
        input_dim: int = 2352,
        hidden_dims: List[int] = [392, 256, 256],
        num_classes: int = 10,
        dropout_p: float = 0.0
    ):
        super().__init__()
        self.input_dim = input_dim
        self.dropout_p = dropout_p

        layers = []
        prev_dim = input_dim

        for hidden_dim in hidden_dims:
            layers.append(nn.Linear(prev_dim, hidden_dim))
            layers.append(nn.ReLU())
            if dropout_p > 0:
                layers.append(nn.Dropout(dropout_p))
            prev_dim = hidden_dim

        layers.append(nn.Linear(prev_dim, num_classes))

        self.network = nn.Sequential(*layers)

        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                if m.bias is not None:
                    nn.init.zeros_(m.bias)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass. x: [B, 3, 28, 28] -> logits: [B, 10]"""
        x = x.view(x.size(0), -1)
        return self.network(x)


def get_model(method: str = "ERM", use_spectral_norm: bool = False) -> SimpleMLP:
    """Factory for method-specific models."""
    dropout_p = 0.5 if method == "Dropout" else 0.0
    model = SimpleMLP(dropout_p=dropout_p)

    if use_spectral_norm or method == "SpectralNorm":
        for name, module in model.named_modules():
            if isinstance(module, nn.Linear):
                nn.utils.spectral_norm(module)

    return model
