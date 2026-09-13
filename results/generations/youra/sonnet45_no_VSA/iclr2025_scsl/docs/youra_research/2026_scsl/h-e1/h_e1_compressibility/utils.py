"""Utility functions for logging, checkpointing, and seed setting."""

import random
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import torch
import numpy as np


def set_seed(seed: int):
    """Set all random seeds for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def save_checkpoint(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    epoch: int,
    metrics: Dict[str, float],
    path: str,
    seed: int,
    method: str,
    config: Optional[Dict[str, Any]] = None
):
    """Save model checkpoint with full state."""
    checkpoint = {
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),
        "epoch": epoch,
        "seed": seed,
        "method": method,
        "metrics": metrics,
        "config": config or {}
    }
    torch.save(checkpoint, path)


def load_checkpoint(
    path: str,
    model: torch.nn.Module,
    optimizer: Optional[torch.optim.Optimizer] = None
) -> Dict[str, Any]:
    """Load checkpoint and restore model state."""
    checkpoint = torch.load(path, map_location="cpu")
    model.load_state_dict(checkpoint["model_state_dict"])
    if optimizer is not None and "optimizer_state_dict" in checkpoint:
        optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
    return checkpoint


def setup_logging(log_dir: str, method: str, seed: int) -> logging.Logger:
    """Setup logging for training."""
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    log_file = Path(log_dir) / f"{method}_seed{seed}_training.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)
