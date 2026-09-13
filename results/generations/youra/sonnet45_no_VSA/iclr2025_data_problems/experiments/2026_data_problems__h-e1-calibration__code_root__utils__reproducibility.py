"""Reproducibility utilities for deterministic experiments."""
import torch
import numpy as np
import random


def set_seed(seed=42):
    """Set random seeds for reproducibility."""
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    random.seed(seed)

    if torch.cuda.is_available():
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
        # Note: use_deterministic_algorithms can cause errors with some operations
        # torch.use_deterministic_algorithms(True)

    print(f"[Reproducibility] Set all random seeds to {seed}")
