"""Data loading module for MNIST and Fashion-MNIST."""

import torch
from torch.utils.data import DataLoader, Dataset
from torchvision import datasets, transforms
from typing import Tuple


def get_transforms(dataset_name: str) -> transforms.Compose:
    """Get dataset-specific normalization.

    Args:
        dataset_name: 'mnist' or 'fashion_mnist'

    Returns:
        Transform pipeline with normalization
    """
    if dataset_name.lower() == "mnist":
        # MNIST mean and std
        return transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.1307,), (0.3081,))
        ])
    elif dataset_name.lower() == "fashion_mnist":
        # Fashion-MNIST normalization
        return transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.5,), (0.5,))
        ])
    else:
        raise ValueError(f"Unknown dataset: {dataset_name}")


def create_seeded_dataloader(
    dataset: Dataset,
    batch_size: int,
    shuffle: bool,
    seed: int,
    num_workers: int = 0
) -> DataLoader:
    """Create DataLoader with deterministic generator.

    Args:
        dataset: PyTorch dataset
        batch_size: Batch size
        shuffle: Whether to shuffle
        seed: Random seed for reproducibility
        num_workers: Number of workers (0 for determinism)

    Returns:
        DataLoader with seeded generator
    """
    generator = torch.Generator()
    generator.manual_seed(seed)

    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        generator=generator
    )


def load_dataset(
    dataset_name: str,
    data_root: str,
    batch_size: int,
    seed: int
) -> Tuple[DataLoader, DataLoader]:
    """Load MNIST or Fashion-MNIST with proper transforms.

    Args:
        dataset_name: 'mnist' or 'fashion_mnist'
        data_root: Root directory for data
        batch_size: Batch size
        seed: Random seed for DataLoader

    Returns:
        (train_loader, test_loader) tuple
    """
    transform = get_transforms(dataset_name)

    if dataset_name.lower() == "mnist":
        train_dataset = datasets.MNIST(
            root=data_root,
            train=True,
            download=True,
            transform=transform
        )
        test_dataset = datasets.MNIST(
            root=data_root,
            train=False,
            download=True,
            transform=transform
        )
    elif dataset_name.lower() == "fashion_mnist":
        train_dataset = datasets.FashionMNIST(
            root=data_root,
            train=True,
            download=True,
            transform=transform
        )
        test_dataset = datasets.FashionMNIST(
            root=data_root,
            train=False,
            download=True,
            transform=transform
        )
    else:
        raise ValueError(f"Unknown dataset: {dataset_name}")

    train_loader = create_seeded_dataloader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        seed=seed
    )
    test_loader = create_seeded_dataloader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
        seed=seed
    )

    return train_loader, test_loader
