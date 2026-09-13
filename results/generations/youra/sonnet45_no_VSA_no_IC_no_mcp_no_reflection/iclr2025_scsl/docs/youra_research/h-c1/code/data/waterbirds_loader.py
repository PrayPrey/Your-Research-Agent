"""Waterbirds dataset loader with group labels."""

import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image
import pandas as pd
from pathlib import Path
from typing import Tuple, Optional, Callable


class WaterbirdDataset(Dataset):
    """Waterbirds dataset with group labels for worst-group accuracy."""

    def __init__(self, root: str, split: str, transform: Optional[Callable] = None):
        """
        Args:
            root: Path to waterbirds root directory
            split: 'train', 'val', or 'test'
            transform: Image transformations
        """
        self.root = Path(root)
        self.split = split
        self.transform = transform

        # Mock dataset for validation - replace with real loader
        self._create_mock_data()

    def _create_mock_data(self):
        """Create mock dataset for code validation."""
        # Group 0: landbird + land (easy correct)
        # Group 1: landbird + water (hard spurious)
        # Group 2: waterbird + land (hard spurious)
        # Group 3: waterbird + water (easy correct)

        if self.split == 'train':
            n_samples = 500
        elif self.split == 'val':
            n_samples = 150
        else:  # test
            n_samples = 600

        self.labels = torch.randint(0, 2, (n_samples,))  # 0=landbird, 1=waterbird
        self.groups = torch.randint(0, 4, (n_samples,))  # 4 groups

        # Simulate spurious correlation: landbird often on land (group 0), waterbird on water (group 3)
        for i in range(n_samples):
            if self.labels[i] == 0:  # landbird
                self.groups[i] = 0 if torch.rand(1) < 0.9 else 1
            else:  # waterbird
                self.groups[i] = 3 if torch.rand(1) < 0.9 else 2

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int, int]:
        """Returns (image, label, group)."""
        # Generate random image (3, 224, 224)
        img = torch.rand(3, 224, 224)

        if self.transform:
            # Transform expects PIL, but mock uses tensor
            pass

        label = self.labels[idx].item()
        group = self.groups[idx].item()

        return img, label, group

    def __len__(self) -> int:
        return len(self.labels)


def get_waterbirds_loader(
    root: str,
    split: str,
    batch_size: int,
    num_workers: int = 2,
    shuffle: bool = None
) -> DataLoader:
    """Create Waterbirds DataLoader with ImageNet normalization."""

    if shuffle is None:
        shuffle = (split == 'train')

    # ImageNet normalization
    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                           std=[0.229, 0.224, 0.225])
    ])

    dataset = WaterbirdDataset(root, split, transform)

    loader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        pin_memory=True
    )

    return loader
