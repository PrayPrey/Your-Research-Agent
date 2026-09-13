"""Data loading module for Waterbirds dataset.

Implements WaterbirdsDataset with group label tracking and deterministic evaluation loader.
Returns (image, label, group_id, sample_idx) from __getitem__.
"""

import os
from typing import Tuple

import numpy as np
import pandas as pd
import torch
from PIL import Image
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms

from config import Config


class WaterbirdsDataset(Dataset):
    """Waterbirds dataset with group label tracking.

    Groups:
        G1 (0): Landbirds on land background (majority)
        G2 (1): Landbirds on water background (minority)
        G3 (2): Waterbirds on water background (majority)
        G4 (3): Waterbirds on land background (minority)
    """

    def __init__(self, root: str, split: str, transform=None):
        """Initialize Waterbirds dataset.

        Args:
            root: Path to waterbird_complete95_forest2water2 directory
            split: One of 'train' (0), 'val' (1), or 'test' (2)
            transform: Image transforms to apply
        """
        self.root = root
        self.transform = transform

        # Load metadata
        metadata_path = os.path.join(root, "metadata.csv")
        self.metadata = pd.read_csv(metadata_path)

        # Filter by split
        split_map = {"train": 0, "val": 1, "test": 2}
        split_idx = split_map[split]
        self.metadata = self.metadata[self.metadata["split"] == split_idx].reset_index(drop=True)

        # Store arrays for fast access
        self.img_filenames = self.metadata["img_filename"].values
        self.labels = self.metadata["y"].values.astype(np.int64)
        self.places = self.metadata["place"].values.astype(np.int64)

        # Compute group_id: y * 2 + place
        # G1: y=0, place=0 -> group_id=0 (landbird on land, majority)
        # G2: y=0, place=1 -> group_id=1 (landbird on water, minority)
        # G3: y=1, place=0 -> group_id=2 (waterbird on land, minority)
        # G4: y=1, place=1 -> group_id=3 (waterbird on water, majority)
        self.group_ids = self.labels * 2 + self.places

    def __len__(self) -> int:
        return len(self.metadata)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int, int, int]:
        """Get item with group tracking.

        Returns:
            Tuple of (image, label, group_id, sample_idx)
        """
        img_path = os.path.join(self.root, self.img_filenames[idx])
        image = Image.open(img_path).convert("RGB")

        if self.transform is not None:
            image = self.transform(image)

        label = int(self.labels[idx])
        group_id = int(self.group_ids[idx])

        return image, label, group_id, idx


def get_train_transforms(config: Config) -> transforms.Compose:
    """Get training data transforms with augmentation."""
    return transforms.Compose([
        transforms.RandomResizedCrop(config.train_crop_size),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize(mean=config.img_mean, std=config.img_std),
    ])


def get_eval_transforms(config: Config) -> transforms.Compose:
    """Get evaluation transforms (deterministic, no augmentation)."""
    return transforms.Compose([
        transforms.Resize(config.eval_resize),
        transforms.CenterCrop(config.eval_crop_size),
        transforms.ToTensor(),
        transforms.Normalize(mean=config.img_mean, std=config.img_std),
    ])


def get_dataloaders(config: Config) -> Tuple[DataLoader, DataLoader, DataLoader]:
    """Get train, validation, and test dataloaders.

    Args:
        config: Experiment configuration

    Returns:
        Tuple of (train_loader, val_loader, test_loader)
    """
    train_transform = get_train_transforms(config)
    eval_transform = get_eval_transforms(config)

    train_dataset = WaterbirdsDataset(
        root=config.data_root,
        split="train",
        transform=train_transform,
    )
    val_dataset = WaterbirdsDataset(
        root=config.data_root,
        split="val",
        transform=eval_transform,
    )
    test_dataset = WaterbirdsDataset(
        root=config.data_root,
        split="test",
        transform=eval_transform,
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=config.batch_size,
        shuffle=True,
        num_workers=config.num_workers,
        pin_memory=config.pin_memory,
        drop_last=False,
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=config.batch_size,
        shuffle=False,
        num_workers=config.num_workers,
        pin_memory=config.pin_memory,
    )
    test_loader = DataLoader(
        test_dataset,
        batch_size=config.batch_size,
        shuffle=False,
        num_workers=config.num_workers,
        pin_memory=config.pin_memory,
    )

    return train_loader, val_loader, test_loader


def get_eval_dataloader(config: Config) -> DataLoader:
    """Get deterministic evaluation dataloader for loss trajectory logging.

    Uses fixed ordering (shuffle=False) and eval transforms for reproducible
    per-sample loss computation.

    Args:
        config: Experiment configuration

    Returns:
        DataLoader for deterministic evaluation
    """
    eval_transform = get_eval_transforms(config)

    eval_dataset = WaterbirdsDataset(
        root=config.data_root,
        split="train",  # Evaluate on training set for trajectory
        transform=eval_transform,
    )

    eval_loader = DataLoader(
        eval_dataset,
        batch_size=config.batch_size,
        shuffle=False,  # Fixed ordering for reproducibility
        num_workers=config.num_workers,
        pin_memory=config.pin_memory,
    )

    return eval_loader


def get_minority_labels(dataset: WaterbirdsDataset) -> np.ndarray:
    """Get binary minority labels from dataset.

    Minority groups: G2 (landbirds on water), G4 (waterbirds on land)
    But based on group_id calculation: G2 is group_id=1, G4 is group_id=2

    Wait, let's recalculate:
    - G1: y=0 (landbird), place=0 (land) -> group_id = 0*2 + 0 = 0 (majority)
    - G2: y=0 (landbird), place=1 (water) -> group_id = 0*2 + 1 = 1 (minority)
    - G3: y=1 (waterbird), place=0 (land) -> group_id = 1*2 + 0 = 2 (minority)
    - G4: y=1 (waterbird), place=1 (water) -> group_id = 1*2 + 1 = 3 (majority)

    Args:
        dataset: WaterbirdsDataset instance

    Returns:
        Binary array where 1 = minority (groups 1, 2), 0 = majority (groups 0, 3)
    """
    # Minority: group_id 1 or 2 (spurious correlation mismatch)
    minority_labels = ((dataset.group_ids == 1) | (dataset.group_ids == 2)).astype(np.int64)
    return minority_labels
