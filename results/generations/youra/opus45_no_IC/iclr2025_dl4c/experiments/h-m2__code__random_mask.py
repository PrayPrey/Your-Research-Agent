"""Random mask generation with sparsity matching for ablation control."""

import torch
from typing import Optional


def create_random_mask(seq_len: int, num_executed: int, device=None, generator: Optional[torch.Generator] = None) -> torch.Tensor:
    """
    Create random binary mask with exactly num_executed ones (sparsity-matched).

    Args:
        seq_len: Sequence length
        num_executed: Number of positions to mark as 1
        device: Target device
        generator: Optional random generator for reproducibility

    Returns:
        mask: [seq_len] binary float tensor with exactly num_executed ones
    """
    if num_executed >= seq_len:
        return torch.ones(seq_len, dtype=torch.float, device=device)
    if num_executed <= 0:
        return torch.zeros(seq_len, dtype=torch.float, device=device)

    perm = torch.randperm(seq_len, generator=generator, device=device)
    mask = torch.zeros(seq_len, dtype=torch.float, device=device)
    mask[perm[:num_executed]] = 1.0
    return mask


def build_random_mask_like(fgo_mask: torch.Tensor, seed: int) -> torch.Tensor:
    """
    Given a trace-based FGO mask, return random mask with same sparsity.

    Args:
        fgo_mask: [seq_len] binary FGO mask (1=executed)
        seed: Random seed for reproducibility

    Returns:
        random_mask: [seq_len] random binary mask with same number of ones
    """
    num_executed = int(fgo_mask.sum().item())
    seq_len = fgo_mask.numel()

    gen = torch.Generator(device=fgo_mask.device).manual_seed(seed)
    return create_random_mask(seq_len, num_executed, device=fgo_mask.device, generator=gen)


def build_batch_random_masks(batch_fgo_masks: torch.Tensor, seed: int) -> torch.Tensor:
    """
    Build random masks for entire batch, matching per-sample sparsity.

    Args:
        batch_fgo_masks: [B, seq_len] FGO masks
        seed: Base seed (per-sample seed = seed + sample_idx)

    Returns:
        random_masks: [B, seq_len] random masks
    """
    B, seq_len = batch_fgo_masks.shape
    random_masks = torch.zeros_like(batch_fgo_masks)

    for i in range(B):
        random_masks[i] = build_random_mask_like(batch_fgo_masks[i], seed + i)

    return random_masks
