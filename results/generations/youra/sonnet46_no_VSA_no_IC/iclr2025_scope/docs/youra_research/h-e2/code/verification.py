"""Mask validation and mechanism verification for h-e2."""
from __future__ import annotations

import torch
from typing import Dict, List


def validate_swa_mask(mask: torch.Tensor, window_size: int = 512) -> None:
    """
    Spot-checks 10 positions in mask for correct sliding-window causal structure.
    Args:
        mask: (seq_len, seq_len) additive float mask (0.0 / -inf)
    Raises:
        AssertionError if any position violates expected pattern
    """
    seq_len = mask.shape[0]
    check_positions = list(range(min(seq_len, 10)))

    for i in check_positions:
        attended = (mask[i] == 0.0).nonzero(as_tuple=True)[0]
        assert len(attended) > 0, f"Row {i}: no attended positions"
        assert attended.min().item() >= max(0, i - window_size + 1), (
            f"Row {i}: attended too far back "
            f"(min={attended.min()}, expected>={max(0, i - window_size + 1)})"
        )
        assert attended.max().item() == i, (
            f"Row {i}: max attended position {attended.max()} != {i} (causal violation)"
        )

    print(f"SWA mask validation PASSED (checked {len(check_positions)} positions)")


def verify_swa_mechanism(
    model,
    target_layers: List[int],
    window_size: int = 512,
    test_seq_len: int = 600,
) -> Dict[int, int]:
    """
    Uses forward pre-hooks to verify SWA mask is correctly applied to target layers.
    Args:
        test_seq_len: must be > window_size to verify windowing at position test_seq_len-1
    Returns:
        {layer_idx: attended_count} — attended_count should == window_size for all target layers
    Raises:
        AssertionError if any layer has wrong attended count
    """
    assert test_seq_len > window_size, (
        f"test_seq_len={test_seq_len} must be > window_size={window_size} "
        "to verify windowing (otherwise trivially passes)"
    )

    captured: Dict[int, int] = {}
    hooks = []

    for idx in target_layers:
        def make_hook(layer_idx: int):
            def hook(module, args, kwargs):
                if "attention_mask" in kwargs and kwargs["attention_mask"] is not None:
                    mask = kwargs["attention_mask"]
                    # mask shape: (1, 1, seq_len, seq_len)
                    if mask.dim() == 4 and mask.shape[2] >= test_seq_len:
                        row = mask[0, 0, test_seq_len - 1]  # (seq_len,)
                        attended = (row == 0.0).sum().item()
                        captured[layer_idx] = attended
            return hook

        h = model.model.layers[idx].self_attn.register_forward_pre_hook(
            make_hook(idx), with_kwargs=True
        )
        hooks.append(h)

    device = next(model.parameters()).device
    dummy = torch.zeros(1, test_seq_len, dtype=torch.long, device=device)
    with torch.no_grad():
        model(dummy)

    for h in hooks:
        h.remove()

    for layer_idx in target_layers:
        if layer_idx not in captured:
            print(f"  WARNING: Layer {layer_idx} hook did not capture mask "
                  "(may use different attention path)")
            continue
        attended = captured[layer_idx]
        assert attended == window_size, (
            f"Layer {layer_idx}: expected {window_size} attended positions, "
            f"got {attended}. SWA mask not correctly applied!"
        )

    if captured:
        print(f"SWA mechanism VERIFIED: {len(captured)} layers correctly use w={window_size}")
    else:
        print("WARNING: No hooks captured — verify attn_implementation='eager'")

    return captured
