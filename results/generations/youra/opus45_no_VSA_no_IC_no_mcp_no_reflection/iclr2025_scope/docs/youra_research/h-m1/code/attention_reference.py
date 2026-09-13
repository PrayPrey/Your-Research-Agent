"""Forward hook capture for BERT attention layer outputs."""

from typing import Dict
import torch
from torch import Tensor
from transformers import BertModel


class AttentionOutputCapture:
    """Registers forward hooks on all 12 BertSelfAttention modules; captures outputs."""

    def __init__(self, bert: BertModel):
        self.bert = bert
        self._cache: Dict[int, Tensor] = {}
        self._hooks = []

        for i, layer in enumerate(bert.encoder.layer):
            hook = layer.attention.self.register_forward_hook(
                lambda mod, inp, out, layer_idx=i: self._cache.__setitem__(layer_idx, out[0])
            )
            self._hooks.append(hook)

    def run_forward(self, input_ids: Tensor) -> None:
        """Run BERT forward pass once, populating cache for all 12 layers."""
        with torch.no_grad():
            self.bert(input_ids)

    def get_layer_output(self, layer_idx: int) -> Tensor:
        """Get cached self-attention output for layer_idx.

        Returns:
            [batch, seq_len, d_model]
        """
        return self._cache.get(layer_idx, None)

    def remove_hooks(self) -> None:
        """Clean up all registered hooks."""
        for hook in self._hooks:
            hook.remove()
        self._hooks.clear()
        self._cache.clear()
