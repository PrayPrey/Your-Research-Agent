"""Data loading module for MNIST with rotation augmentation."""
import torch
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from config import DATA_CONFIG, EXPERIMENT_CONFIG, TRAINING_CONFIG


def get_transform(augmentation_type: str = "baseline") -> transforms.Compose:
    """Get transform pipeline for specified augmentation type.

    Args:
        augmentation_type: "baseline" (normalize only) or "rotation" (±15° + normalize)

    Returns:
        Composed transforms pipeline
    """
    if augmentation_type == "baseline":
        return transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((DATA_CONFIG["mean"],), (DATA_CONFIG["std"],))
        ])
    elif augmentation_type == "rotation":
        return transforms.Compose([
            transforms.RandomRotation(EXPERIMENT_CONFIG["rotation_degrees"]),
            transforms.ToTensor(),
            transforms.Normalize((DATA_CONFIG["mean"],), (DATA_CONFIG["std"],))
        ])
    else:
        raise ValueError(f"Unknown augmentation type: {augmentation_type}")


def get_dataloaders(augmentation_type: str = "baseline", batch_size: int = 64, num_workers: int = 4, seed: int = 42):
    """Create train and test dataloaders for MNIST.

    Args:
        augmentation_type: "baseline" or "rotation"
        batch_size: Batch size for dataloaders
        num_workers: Number of worker processes
        seed: Random seed for reproducibility

    Returns:
        (train_loader, test_loader) where test_loader uses baseline transforms

    Shapes:
        - Batch: [B, 1, 28, 28]
        - Labels: [B]
    """
    # Training transform (augmentation-specific)
    train_transform = get_transform(augmentation_type)

    # Test transform (always baseline, no augmentation)
    test_transform = get_transform("baseline")

    # Load datasets
    train_dataset = datasets.MNIST(
        root=DATA_CONFIG["data_root"],
        train=True,
        download=DATA_CONFIG["download"],
        transform=train_transform
    )

    test_dataset = datasets.MNIST(
        root=DATA_CONFIG["data_root"],
        train=False,
        download=DATA_CONFIG["download"],
        transform=test_transform
    )

    # Create dataloaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=True if torch.cuda.is_available() else False
    )

    test_loader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True if torch.cuda.is_available() else False
    )

    return train_loader, test_loader
