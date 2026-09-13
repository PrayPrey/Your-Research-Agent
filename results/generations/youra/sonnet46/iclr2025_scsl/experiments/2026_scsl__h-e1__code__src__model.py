"""
model.py - get_model() and GradientNormAnalyzer

GradientNormAnalyzer uses a forward hook on model.fc to capture h(x_i) ∈ R^2048,
then computes per-sample gradient norms via outer-product decomposition (no backward needed):
  g_tilde_i = ||p_i - y_i_onehot||   (residual norm)
  g_raw_i   = g_tilde_i * h_norm_i   (raw FC weight gradient norm)
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch import Tensor
from torchvision import models


def get_model(device: torch.device) -> nn.Module:
    """
    ResNet-50 pretrained on ImageNet, FC replaced with Linear(2048, 2).
    BN layers remain in train mode during ERM; caller switches to eval() for collection.
    """
    model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
    model.fc = nn.Linear(2048, 2)
    return model.to(device)


class GradientNormAnalyzer:
    """
    Vectorized per-sample gradient norm via FC forward hook + outer-product decomposition.

    Usage:
        analyzer = GradientNormAnalyzer(model)
        g_raw, g_tilde, h_norm = analyzer.compute_batch_norms(images, labels)
        analyzer.clear()
    """

    def __init__(self, model: nn.Module) -> None:
        self.model = model
        self.features: dict = {}
        self._hook_handle = None
        self._register_hooks()

    def _register_hooks(self) -> None:
        """Register forward hook on model.fc to capture h(x_i) as CPU tensor."""
        def _hook(module, input, output):
            # input[0] is the (B, 2048) feature vector fed into the FC layer
            self.features['fc_input'] = input[0].detach().cpu()

        self._hook_handle = self.model.fc.register_forward_hook(_hook)

    def compute_batch_norms(
        self,
        images: Tensor,   # (B, 3, 224, 224) on device
        labels: Tensor,   # (B,) long, on device
    ) -> tuple:
        """
        Single forward pass, outer-product decomposition. No per-sample backward.

        Steps:
          1. forward pass -> hook fires -> features['fc_input'] = h (B, 2048) on CPU
          2. p = softmax(logits)
          3. residual = p - one_hot(labels)
          4. g_tilde = residual.norm(dim=1)
          5. h_norm  = h.norm(dim=1)
          6. g_raw   = g_tilde * h_norm

        Returns: g_raw (B,), g_tilde (B,), h_norm (B,) — all CPU float32
        """
        with torch.no_grad():
            logits = self.model(images)                         # (B, 2); hook fires

        h = self.features['fc_input']                           # (B, 2048) on CPU
        p = F.softmax(logits.cpu(), dim=1)                      # (B, 2)
        y_oh = F.one_hot(labels.cpu(), num_classes=2).float()   # (B, 2)
        residual = p - y_oh                                     # (B, 2)
        g_tilde = residual.norm(dim=1)                          # (B,)
        h_norm = h.norm(dim=1)                                  # (B,)
        g_raw = g_tilde * h_norm                                # (B,)
        return g_raw, g_tilde, h_norm

    def clear(self) -> None:
        """Clear cached features between batches to avoid memory accumulation."""
        self.features.clear()

    def remove_hooks(self) -> None:
        """Remove the registered forward hook (call on cleanup)."""
        if self._hook_handle is not None:
            self._hook_handle.remove()
            self._hook_handle = None
