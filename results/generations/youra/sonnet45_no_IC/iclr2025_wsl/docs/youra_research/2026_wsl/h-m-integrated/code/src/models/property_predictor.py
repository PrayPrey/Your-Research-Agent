"""
Property Prediction Head (Task A-6)
Predicts model properties (e.g., accuracy) from final embeddings
"""

import torch
import torch.nn as nn
from torch import Tensor


class PropertyPredictor(nn.Module):
    """Property prediction head (accuracy prediction)"""

    def __init__(
        self,
        d_z: int = 256,
        num_properties: int = 1,
        dropout: float = 0.1
    ):
        """
        Args:
            d_z: Input embedding dimension
            num_properties: Number of properties to predict
            dropout: Dropout rate
        """
        super().__init__()
        self.d_z = d_z
        self.num_properties = num_properties

        # 2-layer MLP for property prediction
        self.predictor = nn.Sequential(
            nn.Linear(d_z, 128),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(128, num_properties)
        )

    def forward(self, z_final: Tensor) -> Tensor:
        """
        Predict properties from embeddings.

        Args:
            z_final: [B, d_z] final embeddings
        Returns:
            predictions: [B, num_properties] property predictions
        """
        # Handle both batched and single inputs
        is_batched = (z_final.dim() == 2)
        if not is_batched:
            z_final = z_final.unsqueeze(0)  # [1, d_z]

        predictions = self.predictor(z_final)  # [B, num_properties] or [1, num_properties]

        if not is_batched:
            predictions = predictions.squeeze(0)  # [num_properties]

        return predictions
