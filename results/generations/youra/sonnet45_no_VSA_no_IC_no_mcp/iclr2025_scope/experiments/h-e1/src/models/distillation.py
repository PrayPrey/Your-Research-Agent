import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple, List


class LayerWiseMSELoss(nn.Module):
    """Normalized layer-wise MSE loss for distillation."""

    def __init__(self, epsilon: float = 1e-8):
        super().__init__()
        self.epsilon = epsilon

    def forward(
        self,
        teacher_hiddens: Tuple[torch.Tensor, ...],
        student_hiddens: List[torch.Tensor]
    ) -> Tuple[torch.Tensor, List[torch.Tensor]]:
        """
        Args:
            teacher_hiddens: Tuple of 13 tensors [batch, seq, 768]
            student_hiddens: List of 12 tensors [batch, seq, 768]

        Returns:
            total_loss: Scalar
            layer_losses: List of 12 scalars
        """
        layer_losses = []

        for i in range(12):
            teacher_h = teacher_hiddens[i + 1]  # Skip embedding layer
            student_h = student_hiddens[i]

            # Compute raw MSE
            mse = F.mse_loss(student_h, teacher_h, reduction='mean')

            # Normalize by teacher variance
            teacher_var = torch.var(teacher_h)
            normalized_mse = mse / (teacher_var + self.epsilon)

            layer_losses.append(normalized_mse)

        # Average across layers
        total_loss = torch.mean(torch.stack(layer_losses))

        return total_loss, layer_losses
