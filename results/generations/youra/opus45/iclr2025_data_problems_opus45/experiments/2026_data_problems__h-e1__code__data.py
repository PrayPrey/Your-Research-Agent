"""
Data loading utilities for H-E1 experiment.
CIFAR-10 with subset sampling for LOO feasibility.
"""

import numpy as np
import torch
from torch.utils.data import DataLoader, Subset
from torchvision import transforms
from torchvision.datasets import CIFAR10
from typing import Tuple

from config import ExperimentConfig

NORMALIZE_MEAN = [0.4914, 0.4822, 0.4465]
NORMALIZE_STD = [0.2470, 0.2435, 0.2616]


def get_transform():
    """Standard CIFAR-10 normalization (no augmentation for LOO consistency)."""
    return transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(mean=NORMALIZE_MEAN, std=NORMALIZE_STD)
    ])


def get_subset_indices(cfg: ExperimentConfig) -> np.ndarray:
    """Reproducible 5000-sample subset indices (seed=42)."""
    np.random.seed(cfg.subset_seed)
    indices = np.random.choice(50000, size=cfg.train_subset_size, replace=False)
    return indices


def get_loo_test_indices(cfg: ExperimentConfig) -> np.ndarray:
    """Reproducible 100-sample LOO test indices (seed=42)."""
    np.random.seed(cfg.subset_seed + 1)
    indices = np.random.choice(10000, size=cfg.loo_test_size, replace=False)
    return indices


def get_cifar10_datasets(cfg: ExperimentConfig):
    """Load CIFAR-10 train and test datasets."""
    transform = get_transform()

    train_dataset = CIFAR10(
        root=cfg.data_root,
        train=True,
        download=True,
        transform=transform
    )
    test_dataset = CIFAR10(
        root=cfg.data_root,
        train=False,
        download=True,
        transform=transform
    )

    return train_dataset, test_dataset


def get_cifar10_loaders(cfg: ExperimentConfig) -> Tuple[DataLoader, DataLoader, DataLoader]:
    """
    Returns (train_subset_loader, loo_test_loader, full_test_loader).

    - train_subset_loader: 5000 samples for training
    - loo_test_loader: 100 samples for LOO evaluation
    - full_test_loader: Full test set for general evaluation
    """
    train_dataset, test_dataset = get_cifar10_datasets(cfg)

    train_indices = get_subset_indices(cfg)
    train_subset = Subset(train_dataset, train_indices)

    loo_test_indices = get_loo_test_indices(cfg)
    loo_test_subset = Subset(test_dataset, loo_test_indices)

    train_loader = DataLoader(
        train_subset,
        batch_size=cfg.train_batch_size,
        shuffle=True,
        num_workers=4,
        pin_memory=True
    )

    loo_test_loader = DataLoader(
        loo_test_subset,
        batch_size=cfg.test_batch_size,
        shuffle=False,
        num_workers=4,
        pin_memory=True
    )

    full_test_loader = DataLoader(
        test_dataset,
        batch_size=cfg.test_batch_size,
        shuffle=False,
        num_workers=4,
        pin_memory=True
    )

    return train_loader, loo_test_loader, full_test_loader


def get_train_subset(cfg: ExperimentConfig) -> Subset:
    """Get the training subset (for LOO retraining)."""
    train_dataset, _ = get_cifar10_datasets(cfg)
    train_indices = get_subset_indices(cfg)
    return Subset(train_dataset, train_indices)


def make_loo_loader(
    train_subset: Subset,
    leave_out_idx: int,
    cfg: ExperimentConfig,
) -> DataLoader:
    """Create DataLoader with one sample removed for LOO retraining."""
    all_indices = list(range(len(train_subset)))
    loo_indices = [i for i in all_indices if i != leave_out_idx]
    loo_subset = Subset(train_subset, loo_indices)

    return DataLoader(
        loo_subset,
        batch_size=cfg.train_batch_size,
        shuffle=True,
        num_workers=4,
        pin_memory=True
    )
