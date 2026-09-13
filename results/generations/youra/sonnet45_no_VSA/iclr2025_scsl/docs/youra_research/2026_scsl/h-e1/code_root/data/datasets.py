"""
Dataset implementations for H-E1 SAM+SWA experiment
- ColoredMNIST: Synthetic spurious correlation benchmark
- CelebA: Real-world spurious correlation via WILDS
"""

import os
import torch
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from torchvision import datasets, transforms
import numpy as np
from typing import Tuple, Dict
from pathlib import Path


class ColoredMNIST(Dataset):
    """
    ColoredMNIST spurious correlation benchmark (Arjovsky et al. 2019).
    Background color (Red/Green) is correlated with label in train, anti-correlated in test.
    """

    def __init__(
        self,
        root: str,
        train: bool = True,
        correlation: float = 0.9,
        download: bool = True
    ):
        """
        Args:
            root: Data root directory
            train: Training or test split
            correlation: Probability of color matching label (0.9 train, 0.1 test)
            download: Download MNIST if not present
        """
        self.root = root
        self.train = train
        self.correlation = correlation

        # Load MNIST
        mnist = datasets.MNIST(root=root, train=train, download=download)
        self.data = mnist.data
        self.targets = mnist.targets

        # Binary labels: 0-4 → 0, 5-9 → 1
        self.targets = (self.targets >= 5).long()

        # Subsample and assign colors based on correlation
        self._prepare_colored_mnist()

    def _prepare_colored_mnist(self):
        """Downsample to 14x14, assign colors based on spurious correlation"""
        # Downsample to 14x14
        data_downsampled = F.interpolate(
            self.data.unsqueeze(1).float() / 255.0,
            size=(14, 14),
            mode='bilinear',
            align_corners=False
        )
        self.data = data_downsampled.squeeze(1)

        # Assign colors based on correlation
        n = len(self.data)
        self.colors = torch.zeros(n, dtype=torch.long)

        for i in range(n):
            label = self.targets[i].item()
            # With probability `correlation`, color matches label
            if np.random.rand() < self.correlation:
                self.colors[i] = label  # 0=red, 1=green
            else:
                self.colors[i] = 1 - label

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int, Dict]:
        """
        Returns:
            image: [3, 14, 14] RGB tensor
            label: Binary label (0 or 1)
            metadata: {"color": 0 (red) or 1 (green), "group": 0-3}
        """
        # Get grayscale image
        gray = self.data[idx]  # [14, 14]

        # Create RGB image with colored background
        label = self.targets[idx].item()
        color = self.colors[idx].item()

        # Convert to RGB
        image = torch.zeros(3, 14, 14)
        if color == 0:  # Red background
            image[0, :, :] = 1.0  # R channel
            image[1, :, :] = gray  # Foreground in G
            image[2, :, :] = gray  # Foreground in B
        else:  # Green background
            image[0, :, :] = gray
            image[1, :, :] = 1.0  # G channel
            image[2, :, :] = gray

        # Group ID: label * 2 + color (0-3)
        group = label * 2 + color

        metadata = {"color": color, "group": group}

        return image, label, metadata


def get_celeba_loaders(
    root_dir: str,
    batch_size: int = 64,
    num_workers: int = 4,
    download: bool = True
) -> Tuple[DataLoader, DataLoader, DataLoader]:
    """
    Load CelebA dataset via WILDS package.

    Args:
        root_dir: Root directory for WILDS datasets
        batch_size: Batch size
        num_workers: Number of data loading workers
        download: Download if not present

    Returns:
        train_loader, val_loader, test_loader
    """
    try:
        from wilds import get_dataset
    except ImportError:
        raise ImportError("WILDS package required. Install with: pip install wilds")

    # Create root directory if it doesn't exist
    Path(root_dir).mkdir(parents=True, exist_ok=True)

    # Load CelebA from WILDS
    dataset = get_dataset(dataset="celebA", download=download, root_dir=root_dir)

    # Get train/val/test splits
    train_data = dataset.get_subset("train")
    val_data = dataset.get_subset("val")
    test_data = dataset.get_subset("test")

    # Image transforms (ImageNet normalization)
    train_transform = transforms.Compose([
        transforms.Resize(256),
        transforms.RandomCrop(224),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])

    test_transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])

    # Wrap datasets with transforms
    train_data.transform = train_transform
    val_data.transform = test_transform
    test_data.transform = test_transform

    # Create data loaders
    train_loader = DataLoader(
        train_data,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=True
    )

    val_loader = DataLoader(
        val_data,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True
    )

    test_loader = DataLoader(
        test_data,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True
    )

    return train_loader, val_loader, test_loader


def get_dataloaders(
    dataset_name: str,
    batch_size: int,
    root_dir: str,
    num_workers: int = 4
) -> Dict[str, DataLoader]:
    """
    Get train/val/test dataloaders for specified dataset.

    Args:
        dataset_name: "ColoredMNIST" or "CelebA"
        batch_size: Batch size
        root_dir: Root directory for datasets
        num_workers: Number of data loading workers

    Returns:
        Dictionary with "train", "val", "test" DataLoaders
    """
    if dataset_name == "ColoredMNIST":
        # Training data (90% correlation)
        train_dataset = ColoredMNIST(
            root=root_dir,
            train=True,
            correlation=0.9,
            download=True
        )

        # Test data (10% correlation = 90% anti-correlation)
        test_dataset = ColoredMNIST(
            root=root_dir,
            train=False,
            correlation=0.1,
            download=True
        )

        # Split train into train/val (90%/10%)
        train_size = int(0.9 * len(train_dataset))
        val_size = len(train_dataset) - train_size
        train_subset, val_subset = torch.utils.data.random_split(
            train_dataset, [train_size, val_size]
        )

        train_loader = DataLoader(
            train_subset,
            batch_size=batch_size,
            shuffle=True,
            num_workers=num_workers,
            pin_memory=True
        )

        val_loader = DataLoader(
            val_subset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=True
        )

        test_loader = DataLoader(
            test_dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=True
        )

        return {
            "train": train_loader,
            "val": val_loader,
            "test": test_loader
        }

    elif dataset_name == "CelebA":
        train_loader, val_loader, test_loader = get_celeba_loaders(
            root_dir=root_dir,
            batch_size=batch_size,
            num_workers=num_workers
        )
        return {
            "train": train_loader,
            "val": val_loader,
            "test": test_loader
        }

    else:
        raise ValueError(f"Unknown dataset: {dataset_name}")
