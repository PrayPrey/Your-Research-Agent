"""
Data loading utilities for spurious correlation benchmarks
"""
import os
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, datasets
from PIL import Image
import pandas as pd
from collections import defaultdict


class ColoredMNIST(Dataset):
    """Colored MNIST with spurious color-label correlations"""

    def __init__(self, root, train=True, spurious_correlation=0.9, seed=42):
        self.root = root
        self.train = train
        self.spurious_correlation = spurious_correlation

        # Load MNIST
        mnist = datasets.MNIST(root, train=train, download=True)
        self.data = mnist.data.numpy()
        self.targets = mnist.targets.numpy()

        # Create spurious correlation: color correlated with digit < 5 or >= 5
        np.random.seed(seed)
        self.colors = self._create_spurious_colors()

        # Create groups: (label_group, color_group)
        self.groups = self._create_groups()

    def _create_spurious_colors(self):
        """Create spurious color labels"""
        n_samples = len(self.targets)
        colors = np.zeros(n_samples, dtype=np.int64)

        for i in range(n_samples):
            label = self.targets[i]
            # Binary label: 0 if digit < 5, 1 if digit >= 5
            binary_label = int(label >= 5)

            # With probability spurious_correlation, color matches binary label
            if np.random.rand() < self.spurious_correlation:
                colors[i] = binary_label
            else:
                colors[i] = 1 - binary_label

        return colors

    def _create_groups(self):
        """Create group labels for evaluation"""
        groups = np.zeros(len(self.targets), dtype=np.int64)
        for i in range(len(self.targets)):
            binary_label = int(self.targets[i] >= 5)
            # Group encoding: 2 * binary_label + color
            groups[i] = 2 * binary_label + self.colors[i]
        return groups

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        img = self.data[idx]
        target = int(self.targets[idx] >= 5)  # Binary classification
        color = self.colors[idx]
        group = self.groups[idx]

        # Convert grayscale to RGB with spurious color
        img = Image.fromarray(img.astype(np.uint8), mode='L')
        img = img.convert('RGB')
        img_array = np.array(img)

        # Apply color: red (color=0) or green (color=1)
        if color == 0:  # Red
            img_array[:, :, 0] = np.minimum(img_array[:, :, 0] + 100, 255)
        else:  # Green
            img_array[:, :, 1] = np.minimum(img_array[:, :, 1] + 100, 255)

        img = Image.fromarray(img_array.astype(np.uint8))

        # Apply transforms
        transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
        ])
        img = transform(img)

        return img, target, group


class WaterbirdsDataset(Dataset):
    """Waterbirds dataset with background spurious correlation"""

    def __init__(self, root, split='train', transform=None):
        self.root = root
        self.split = split
        self.transform = transform

        # Create synthetic Waterbirds-like dataset
        # In real setting, this would load actual Waterbirds data
        self._create_synthetic_data()

    def _create_synthetic_data(self):
        """Create synthetic waterbirds-like data for testing"""
        n_samples = 1000 if self.split == 'train' else 300

        # Generate synthetic features and labels
        np.random.seed(42 if self.split == 'train' else 43)

        # Binary classification: waterbird (0) vs landbird (1)
        self.targets = np.random.randint(0, 2, n_samples)

        # Spurious background: water (0) vs land (1)
        # Strong correlation in training
        if self.split == 'train':
            spurious_corr = 0.95
        else:
            spurious_corr = 0.5  # Balanced test set

        self.backgrounds = np.zeros(n_samples, dtype=np.int64)
        for i in range(n_samples):
            if np.random.rand() < spurious_corr:
                self.backgrounds[i] = self.targets[i]
            else:
                self.backgrounds[i] = 1 - self.targets[i]

        # Groups: 2 * target + background
        self.groups = 2 * self.targets + self.backgrounds

        # Generate synthetic images (random noise for simplicity)
        self.images = []
        for i in range(n_samples):
            img = np.random.randn(3, 64, 64).astype(np.float32)
            self.images.append(img)

    def __len__(self):
        return len(self.targets)

    def __getitem__(self, idx):
        img = self.images[idx]
        target = self.targets[idx]
        group = self.groups[idx]

        if self.transform:
            img = self.transform(img)
        else:
            img = torch.FloatTensor(img)

        return img, target, group


def get_data_loaders(config):
    """Get data loaders for specified dataset"""

    if config.dataset_name == 'colored_mnist':
        train_dataset = ColoredMNIST(
            config.data_dir,
            train=True,
            spurious_correlation=0.95
        )
        val_dataset = ColoredMNIST(
            config.data_dir,
            train=False,
            spurious_correlation=0.1  # Low correlation for validation
        )
        test_dataset = val_dataset

    elif config.dataset_name == 'waterbirds':
        train_dataset = WaterbirdsDataset(
            config.data_dir,
            split='train'
        )
        val_dataset = WaterbirdsDataset(
            config.data_dir,
            split='val'
        )
        test_dataset = WaterbirdsDataset(
            config.data_dir,
            split='test'
        )

    else:
        raise ValueError(f"Unknown dataset: {config.dataset_name}")

    train_loader = DataLoader(
        train_dataset,
        batch_size=config.batch_size,
        shuffle=True,
        num_workers=config.num_workers,
        pin_memory=True
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=config.batch_size,
        shuffle=False,
        num_workers=config.num_workers,
        pin_memory=True
    )

    test_loader = DataLoader(
        test_dataset,
        batch_size=config.batch_size,
        shuffle=False,
        num_workers=config.num_workers,
        pin_memory=True
    )

    return train_loader, val_loader, test_loader


def get_group_info(dataset):
    """Get group information from dataset"""
    groups = []
    targets = []

    for i in range(len(dataset)):
        _, target, group = dataset[i]
        targets.append(target)
        groups.append(group)

    targets = np.array(targets)
    groups = np.array(groups)

    # Count samples per group
    unique_groups = np.unique(groups)
    group_counts = {g: np.sum(groups == g) for g in unique_groups}

    return targets, groups, group_counts
