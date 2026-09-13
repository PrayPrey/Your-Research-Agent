"""Data loading with seed-controlled reproducibility."""
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
from typing import Tuple
import torch
import numpy as np
import random
import sys
sys.path.append('/workspace/TEST_scsl/docs/youra_research/h-m/code')
from config import DATA_CONFIG, EXPERIMENT_CONFIG


def set_seed(seed: int):
    """
    Set all random seeds for reproducibility.

    Args:
        seed: Random seed value
    """
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    random.seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def get_transform(condition: str, train: bool = True) -> transforms.Compose:
    """
    Get transform pipeline.

    Args:
        condition: "baseline" | "flip30" | "flip50" | "flip90" | "rotation"
        train: If False, return baseline transform (test always clean)

    Returns:
        Transform pipeline
    """
    # Base transforms (always applied)
    base_transforms = [
        transforms.ToTensor(),
        transforms.Normalize(
            mean=(DATA_CONFIG["mean"],),
            std=(DATA_CONFIG["std"],)
        )
    ]

    # Test set always uses baseline
    if not train:
        return transforms.Compose(base_transforms)

    # Condition-specific augmentation
    if condition == "baseline":
        return transforms.Compose(base_transforms)

    elif condition == "flip30":
        return transforms.Compose([
            transforms.RandomHorizontalFlip(p=0.3),
            *base_transforms
        ])

    elif condition == "flip50":
        return transforms.Compose([
            transforms.RandomHorizontalFlip(p=0.5),
            *base_transforms
        ])

    elif condition == "flip90":
        return transforms.Compose([
            transforms.RandomHorizontalFlip(p=0.9),
            *base_transforms
        ])

    elif condition == "rotation":
        return transforms.Compose([
            transforms.RandomRotation(degrees=EXPERIMENT_CONFIG["rotation_degrees"]),
            *base_transforms
        ])

    else:
        raise ValueError(f"Unknown condition: {condition}")


def get_dataloaders(condition: str, batch_size: int = 64, seed: int = 42) -> Tuple[DataLoader, DataLoader]:
    """
    Get dataloaders with seed-controlled sampling (EXTENDED from h-e1).

    Args:
        condition: "baseline" | "flip30" | "flip50" | "flip90" | "rotation"
        batch_size: Batch size
        seed: Random seed for reproducibility (NEW parameter)

    Returns:
        (train_loader, test_loader)
    """
    # Set seed BEFORE data loading
    set_seed(seed)

    # Get transforms
    train_transform = get_transform(condition, train=True)
    test_transform = get_transform("baseline", train=False)

    # Load datasets
    train_dataset = datasets.MNIST(
        root=DATA_CONFIG["data_root"],
        train=True,
        transform=train_transform,
        download=DATA_CONFIG["download"]
    )

    test_dataset = datasets.MNIST(
        root=DATA_CONFIG["data_root"],
        train=False,
        transform=test_transform,
        download=DATA_CONFIG["download"]
    )

    # Create dataloaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=DATA_CONFIG["num_workers"]
    )

    test_loader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=DATA_CONFIG["num_workers"]
    )

    return train_loader, test_loader
