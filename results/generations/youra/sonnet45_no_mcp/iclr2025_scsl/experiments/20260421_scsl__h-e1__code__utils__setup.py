"""
Setup utilities for reproducibility and data downloading
"""

import os
import random
import numpy as np
import torch


def set_seed(seed=42):
    """Set random seeds for reproducibility"""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def download_waterbirds(data_dir):
    """
    Download Waterbirds dataset.

    This is a placeholder - actual download requires accessing the group_DRO repository.
    For now, we check if the dataset exists.

    Args:
        data_dir: Target directory

    Returns:
        success: Boolean indicating if dataset is available
    """
    metadata_path = os.path.join(data_dir, 'metadata.csv')

    if os.path.exists(metadata_path):
        print(f"✓ Waterbirds dataset found at {data_dir}")
        return True
    else:
        print(f"✗ Waterbirds dataset not found at {data_dir}")
        print(f"\nPlease download the dataset:")
        print(f"1. Clone: https://github.com/kohpangwei/group_DRO")
        print(f"2. Follow dataset download instructions")
        print(f"3. Place in: {data_dir}")
        return False


def create_directories(config):
    """Create necessary directories"""
    os.makedirs(config['checkpoint_dir'], exist_ok=True)
    os.makedirs(config['results_dir'], exist_ok=True)
    os.makedirs(config['figures_dir'], exist_ok=True)
    print(f"✓ Created directories")
