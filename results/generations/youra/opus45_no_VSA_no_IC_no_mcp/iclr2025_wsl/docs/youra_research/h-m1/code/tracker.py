from collections import defaultdict
from typing import Dict, List, Optional
import copy

import torch
import torch.nn as nn
from torch import Tensor


class TrainingDynamicsTracker:
    """Track gradient norms, weight updates, and attention entropy during training."""

    def __init__(self, model: nn.Module, model_type: str):
        self.model = model
        self.model_type = model_type
        self.grad_norms: Dict[str, List[float]] = defaultdict(list)
        self.weight_updates: Dict[str, List[float]] = defaultdict(list)
        self.attention_entropy: List[float] = []
        self.prev_weights: Optional[Dict[str, Tensor]] = None

    def track_gradients(self, epoch: int) -> None:
        """Record per-layer gradient norms after backward pass."""
        for name, param in self.model.named_parameters():
            if param.grad is not None:
                norm = param.grad.norm().item()
                self.grad_norms[name].append(norm)

    def snapshot_weights(self) -> Dict[str, Tensor]:
        """Snapshot current weights for delta computation."""
        return {name: param.data.clone() for name, param in self.model.named_parameters()}

    def track_weight_updates(self, prev_weights: Dict[str, Tensor], epoch: int) -> None:
        """Compute weight delta magnitudes from previous snapshot."""
        for name, param in self.model.named_parameters():
            if name in prev_weights:
                delta = (param.data - prev_weights[name]).norm().item()
                self.weight_updates[name].append(delta)

    def track_attention(self, sample_input: List[Tensor]) -> None:
        """NFT only: compute attention entropy."""
        if self.model_type != "nft":
            return
        if not hasattr(self.model, "get_attention_weights"):
            return

        attn = self.model.get_attention_weights(sample_input)
        # attn shape: [batch, heads, seq, seq] - take mean across batch/heads
        attn_mean = attn.mean(dim=(0, 1))
        # Compute entropy: -sum(p * log(p))
        eps = 1e-8
        entropy = -torch.sum(attn_mean * torch.log(attn_mean + eps)).item()
        self.attention_entropy.append(entropy)

    def to_dict(self) -> Dict:
        """Export tracked data."""
        return {
            "model_type": self.model_type,
            "grad_norms": dict(self.grad_norms),
            "weight_updates": dict(self.weight_updates),
            "attention_entropy": self.attention_entropy,
        }
