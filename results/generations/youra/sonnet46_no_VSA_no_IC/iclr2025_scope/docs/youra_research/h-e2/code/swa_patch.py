"""SWA Mask construction and monkey-patching for h-e2.

Implements entropy-guided sliding window attention replacement for Llama-2-7B.
Uses additive float mask (0.0 attend / -inf block) compatible with eager attention.
"""
from __future__ import annotations

import torch
from typing import List


def make_sliding_window_causal_mask(
    seq_len: int,
    window_size: int,
    dtype: torch.dtype,
    device: torch.device,
) -> torch.Tensor:
    """
    Build additive causal sliding-window attention mask.

    Returns:
        mask: shape (seq_len, seq_len), dtype=dtype
              mask[i, j] = 0.0   if j in [max(0, i-window_size+1), i]
              mask[i, j] = -inf  otherwise
    """
    idx = torch.arange(seq_len, device=device)
    row = idx.unsqueeze(1)   # (seq_len, 1)
    col = idx.unsqueeze(0)   # (1, seq_len)
    attend = (col <= row) & (col >= row - window_size + 1)
    mask = torch.where(
        attend,
        torch.zeros(1, dtype=dtype, device=device),
        torch.full((1,), float("-inf"), dtype=dtype, device=device),
    )
    return mask  # (seq_len, seq_len)


def patch_layer_with_swa(layer, window_size: int = 512) -> None:
    """
    Monkey-patches layer.self_attn.forward IN-PLACE with SWA mask injection.
    Original forward is captured via closure.
    Guard against double-patching via _swa_patched attribute.
    """
    if getattr(layer.self_attn, "_swa_patched", False):
        print(f"  Layer already patched, skipping double-patch")
        return

    original_forward = layer.self_attn.forward

    def swa_forward(hidden_states, attention_mask=None, position_ids=None, **kwargs):
        seq_len = hidden_states.shape[1]
        swa_mask = make_sliding_window_causal_mask(
            seq_len=seq_len,
            window_size=window_size,
            dtype=hidden_states.dtype,
            device=hidden_states.device,
        )
        # Shape: (1, 1, seq_len, seq_len) — broadcast over batch and heads
        return original_forward(
            hidden_states,
            attention_mask=swa_mask.unsqueeze(0).unsqueeze(0),
            position_ids=position_ids,
            **kwargs,
        )

    layer.self_attn.forward = swa_forward
    layer.self_attn._swa_patched = True


def apply_entropy_guided_swa(
    model,
    entropy_layer_ranking: List[int],
    k: int = 4,
    window_size: int = 512,
) -> List[int]:
    """
    Patches top-k entropy layers with SWA mask.
    Args:
        entropy_layer_ranking: layer indices sorted by entropy descending (from h-e1)
        k: number of layers to convert
    Returns:
        target_layers: list of k patched layer indices (for diagnostic logging + h-m2)
    """
    assert k <= len(entropy_layer_ranking), (
        f"k={k} exceeds available layers {len(entropy_layer_ranking)}"
    )
    target_layers = entropy_layer_ranking[:k]
    print(f"Converting layers {target_layers} to SWA(w={window_size})")
    for layer_idx in target_layers:
        patch_layer_with_swa(model.model.layers[layer_idx], window_size=window_size)
    return target_layers
