"""
Region masking for spurious/core feature separation.
"""

import torch
import torch.nn.functional as F


def create_spurious_mask(
    images: torch.Tensor,
    dataset_name: str,
    target_size: tuple[int, int]
) -> torch.Tensor:
    """
    Create binary mask for spurious region.

    Waterbirds: background region (inverse of core).

    Args:
        images: [B, 3, 224, 224]
        dataset_name: Dataset name
        target_size: (H, W) for downsampling to match GradCAM

    Returns:
        mask: [B, H, W] binary mask (1=spurious, 0=other)
    """
    batch_size = images.shape[0]
    device = images.device

    if dataset_name == 'Waterbirds':
        # Simplified: outer region as background
        mask = torch.ones(batch_size, 224, 224, device=device)
        mask[:, 56:168, 56:168] = 0  # Center region = bird (zero out)
    elif dataset_name == 'CMNIST':
        # Simplified: use color channels as spurious (outer pixels with higher color intensity)
        # Fallback: outer region mask
        mask = torch.ones(batch_size, 224, 224, device=device)
        mask[:, 56:168, 56:168] = 0  # Zero out center (digit core)
    else:
        raise ValueError(f"Dataset {dataset_name} not implemented for h-e3 PoC")

    # Downsample to target size
    mask_down = downsample_mask(mask, target_size)
    return mask_down


def create_core_mask(
    images: torch.Tensor,
    dataset_name: str,
    target_size: tuple[int, int]
) -> torch.Tensor:
    """
    Create binary mask for core region.

    Waterbirds: center region as bird (simplified).

    Args:
        images: [B, 3, 224, 224]
        dataset_name: Dataset name
        target_size: (H, W) for downsampling

    Returns:
        mask: [B, H, W] binary mask (1=core, 0=other)
    """
    batch_size = images.shape[0]
    device = images.device

    if dataset_name == 'Waterbirds':
        # Simplified: center region as bird
        mask = torch.zeros(batch_size, 224, 224, device=device)
        mask[:, 56:168, 56:168] = 1  # Center region
    elif dataset_name == 'CMNIST':
        # Core mask: center region containing digit shape
        mask = torch.zeros(batch_size, 224, 224, device=device)
        mask[:, 56:168, 56:168] = 1  # Center region (digit)
    else:
        raise ValueError(f"Dataset {dataset_name} not implemented for h-e3 PoC")

    # Downsample to target size
    mask_down = downsample_mask(mask, target_size)
    return mask_down


def downsample_mask(mask: torch.Tensor, target_size: tuple[int, int]) -> torch.Tensor:
    """
    Resize mask to match GradCAM attribution size.

    Args:
        mask: [B, H, W] binary mask
        target_size: (H', W')

    Returns:
        mask_down: [B, H', W']
    """
    mask_resized = F.interpolate(
        mask.unsqueeze(1).float(),
        size=target_size,
        mode='nearest'
    ).squeeze(1)
    return mask_resized
