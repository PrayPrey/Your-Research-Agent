"""MNIST dataset loading with flip augmentation conditions"""
from typing import Tuple
import sys
from pathlib import Path
import torch
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import DataConfig


def create_transform(flip_prob: float, mean: Tuple[float, ...], std: Tuple[float, ...]) -> transforms.Compose:
    """Create transform pipeline with specified flip probability.

    Args:
        flip_prob: Horizontal flip probability [0.0, 1.0]
        mean: Normalization mean
        std: Normalization std

    Returns:
        Transform pipeline
    """
    transform_list = []

    if flip_prob > 0:
        transform_list.append(transforms.RandomHorizontalFlip(p=flip_prob))

    transform_list.extend([
        transforms.ToTensor(),
        transforms.Normalize(mean, std)
    ])

    return transforms.Compose(transform_list)


def get_dataloaders(
    config: DataConfig,
    flip_prob: float
) -> Tuple[DataLoader, DataLoader]:
    """Get MNIST train/test dataloaders.

    Args:
        config: Data configuration
        flip_prob: Flip probability for training set

    Returns:
        (train_loader, test_loader)
    """
    # Training transform with flip augmentation
    train_transform = create_transform(flip_prob, config.mean, config.std)

    # Test transform without augmentation
    test_transform = create_transform(0.0, config.mean, config.std)

    # Load datasets
    train_dataset = datasets.MNIST(
        root=config.data_root,
        train=True,
        download=True,
        transform=train_transform
    )

    test_dataset = datasets.MNIST(
        root=config.data_root,
        train=False,
        download=True,
        transform=test_transform
    )

    # Create dataloaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=config.batch_size,
        shuffle=True,
        num_workers=config.num_workers,
        pin_memory=config.pin_memory
    )

    test_loader = DataLoader(
        test_dataset,
        batch_size=config.batch_size,
        shuffle=False,
        num_workers=config.num_workers,
        pin_memory=config.pin_memory
    )

    return train_loader, test_loader
