"""Waterbirds dataset loader"""

import os
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image
import pandas as pd
from pathlib import Path

class WaterbirdsDataset(Dataset):
    """Waterbirds dataset with group labels"""

    def __init__(self, root_dir: str, split: str = "train", transform=None):
        """
        Args:
            root_dir: Root directory of Waterbirds dataset
            split: One of "train", "val", "test"
            transform: Optional transform to apply to images
        """
        self.root_dir = Path(root_dir)
        self.split = split
        self.transform = transform

        # Load metadata
        metadata_path = self.root_dir / "metadata.csv"
        if not metadata_path.exists():
            raise FileNotFoundError(f"Metadata not found: {metadata_path}")

        self.metadata = pd.read_csv(metadata_path)

        # Filter by split
        split_map = {"train": 0, "val": 1, "test": 2}
        if split not in split_map:
            raise ValueError(f"Invalid split: {split}")

        self.metadata = self.metadata[self.metadata["split"] == split_map[split]]
        self.metadata = self.metadata.reset_index(drop=True)

    def __len__(self):
        return len(self.metadata)

    def __getitem__(self, idx):
        row = self.metadata.iloc[idx]

        # Load image
        img_path = self.root_dir / row["img_filename"]
        image = Image.open(img_path).convert("RGB")

        if self.transform:
            image = self.transform(image)

        # Get labels
        label = int(row["y"])  # Bird class (0=landbird, 1=waterbird)
        place = int(row["place"])  # Background (0=land, 1=water)
        group = int(row["y"]) * 2 + int(row["place"])  # Group: 0,1,2,3

        return image, label, group


def get_waterbirds_dataloader(
    root_dir: str = "/home/anonymous/data/waterbirds_v1.0",
    split: str = "train",
    batch_size: int = 128,
    shuffle: bool = False,
    num_workers: int = 4,
    image_size: int = 224
) -> DataLoader:
    """
    Load Waterbirds dataset with group labels.

    Args:
        root_dir: Root directory of dataset
        split: One of "train", "val", "test"
        batch_size: Batch size
        shuffle: Whether to shuffle
        num_workers: Number of worker processes
        image_size: Image size for transforms

    Returns:
        DataLoader yielding (images, labels, groups)
    """
    # Define transforms
    if split == "train":
        transform = transforms.Compose([
            transforms.Resize((image_size, image_size)),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                std=[0.229, 0.224, 0.225])
        ])
    else:
        transform = transforms.Compose([
            transforms.Resize((image_size, image_size)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                std=[0.229, 0.224, 0.225])
        ])

    dataset = WaterbirdsDataset(root_dir, split, transform)

    dataloader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        pin_memory=True
    )

    return dataloader
