"""Checkpoint loading utilities"""

import os
import torch
from typing import Dict

def load_checkpoint(
    checkpoint_path: str,
    device: str = "cuda"
) -> Dict[str, torch.Tensor]:
    """
    Load checkpoint from disk.

    Args:
        checkpoint_path: Path to .pt file
        device: Device to load tensors

    Returns:
        state_dict: Dict mapping layer names → tensors

    Raises:
        FileNotFoundError: If checkpoint doesn't exist
        RuntimeError: If checkpoint is corrupted
    """
    if not os.path.exists(checkpoint_path):
        raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")

    try:
        checkpoint = torch.load(checkpoint_path, map_location=device)
    except Exception as e:
        raise RuntimeError(f"Failed to load checkpoint: {e}")

    # Handle different checkpoint formats
    if isinstance(checkpoint, dict):
        if "state_dict" in checkpoint:
            return checkpoint["state_dict"]
        elif "model" in checkpoint:
            return checkpoint["model"]
        else:
            # Assume it's already a state_dict
            return checkpoint
    else:
        raise RuntimeError(f"Unexpected checkpoint format: {type(checkpoint)}")
