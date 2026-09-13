import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.models as models
from typing import Optional


def build_resnet50(num_classes: int = 2) -> nn.Module:
    model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
    model.fc = nn.Linear(2048, num_classes)
    return model


class GradientNormTracker:
    def __init__(self, model: nn.Module, target_layer: nn.Module):
        self.activations: Optional[torch.Tensor] = None
        self.gradients: Optional[torch.Tensor] = None
        self._fwd_handle = target_layer.register_forward_hook(self._save_activation)
        self._bwd_handle = target_layer.register_full_backward_hook(self._save_gradient)

    def _save_activation(self, module: nn.Module, input: tuple, output: torch.Tensor) -> None:
        self.activations = output.detach()

    def _save_gradient(self, module: nn.Module, grad_input: tuple, grad_output: tuple) -> None:
        self.gradients = grad_output[0].detach()

    def compute_gradient_norms_by_group(self, spurious_aligned: torch.Tensor) -> tuple:
        if self.gradients is None:
            return 0.0, 0.0

        grad = self.gradients
        B = grad.shape[0]

        per_sample_norm = grad.view(B, -1).norm(dim=1)

        spurious_idx = spurious_aligned.bool()
        minority_idx = ~spurious_idx

        spurious_norm = per_sample_norm[spurious_idx].mean().item() if spurious_idx.sum() > 0 else 0.0
        minority_norm = per_sample_norm[minority_idx].mean().item() if minority_idx.sum() > 0 else 0.0

        return spurious_norm, minority_norm

    def remove_hooks(self) -> None:
        self._fwd_handle.remove()
        self._bwd_handle.remove()
