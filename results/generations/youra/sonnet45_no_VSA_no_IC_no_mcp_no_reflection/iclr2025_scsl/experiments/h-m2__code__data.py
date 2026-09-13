"""
Data infrastructure for h-m2: CMNIST fallback (Waterbirds download failed).
Reuses ColoredMNIST from h-e1.
"""

from dataclasses import dataclass
from typing import Literal
import torch
from torch.utils.data import DataLoader, Dataset
from torchvision import datasets, transforms
import torchvision.transforms.functional as TF
import numpy as np


@dataclass
class DatasetConfig:
    name: str
    batch_size: int
    num_workers: int = 4


class ColoredMNIST(Dataset):
    """CMNIST: MNIST with color bias injection (reused from h-e1)."""
    def __init__(self, root: str, train: bool = True, color_flip_prob: float = 0.25, subset_fraction: float = 1.0):
        self.mnist = datasets.MNIST(root, train=train, download=True)
        self.color_flip_prob = color_flip_prob
        self.subset_fraction = subset_fraction

        # Create subset if requested (for PoC validation)
        if subset_fraction < 1.0:
            import random
            random.seed(42)
            n_samples = int(len(self.mnist) * subset_fraction)
            self.indices = random.sample(range(len(self.mnist)), n_samples)
        else:
            self.indices = None

        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])

    def __len__(self):
        return len(self.indices) if self.indices else len(self.mnist)

    def __getitem__(self, idx):
        if self.indices:
            idx = self.indices[idx]
        img, label = self.mnist[idx]
        img_array = np.array(img)

        # Binary label: 0-4 → 0, 5-9 → 1
        binary_label = 0 if label < 5 else 1

        # Color assignment: red for 0-4, green for 5-9, flipped with prob
        color_label = binary_label
        if np.random.rand() < self.color_flip_prob:
            color_label = 1 - color_label

        # Create RGB image with color bias
        colored = np.zeros((224, 224, 3), dtype=np.uint8)
        img_resized = np.array(TF.resize(TF.to_pil_image(img_array), (224, 224)))

        if color_label == 0:  # Red channel
            colored[:, :, 0] = img_resized
        else:  # Green channel
            colored[:, :, 1] = img_resized

        colored_pil = TF.to_pil_image(colored)
        return self.transform(colored_pil), binary_label


def get_cmnist_dataloader(
    batch_size: int = 128,
    split: Literal['train', 'val', 'test'] = 'train',
    num_workers: int = 4,
    subset_fraction: float = 0.1  # Use 10% for faster PoC
) -> DataLoader:
    """
    Load ColoredMNIST dataset.

    Args:
        batch_size: Batch size
        split: 'train', 'val', or 'test'
        num_workers: Number of data loading workers
        subset_fraction: Fraction of dataset to use

    Returns:
        DataLoader yielding (images, labels)
        images: [B, 3, 224, 224]
        labels: [B] (0=0-4, 1=5-9)
    """
    train_mode = (split == 'train')
    dataset = ColoredMNIST(root='./data/mnist', train=train_mode, subset_fraction=subset_fraction)

    # Split train into train/val if needed
    if split == 'val':
        total = len(dataset)
        val_size = int(0.1 * total)
        _, dataset = torch.utils.data.random_split(dataset, [total - val_size, val_size])

    loader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=(split == 'train'),
        num_workers=num_workers,
        pin_memory=True
    )
    return loader
