"""ColoredMNIST dataset implementation."""

from typing import Tuple, Dict
from pathlib import Path
import torch
from torch.utils.data import Dataset, DataLoader
import torchvision.datasets as datasets
import numpy as np


DATASET_CONFIG = {
    "name": "ColoredMNIST",
    "rho": 0.95,
    "train_size": 50000,
    "val_size": 10000,
    "test_size": 10000,
    "test_correlation_reversed": True,
    "cache_path": "./data/colored_mnist_rho095.pt",
    "image_size": (28, 28, 3),
    "num_classes": 10,
    "num_colors": 2,
    "num_groups": 20
}

DATALOADER_CONFIG = {
    "batch_size": 256,
    "num_workers": 4,
    "pin_memory": True,
    "shuffle_train": True,
    "shuffle_val": False,
    "shuffle_test": False,
    "drop_last": False
}


class ColoredMNIST(Dataset):
    """ColoredMNIST dataset with spurious correlation."""

    def __init__(self, root: str, train: bool, rho: float = 0.95, val: bool = False):
        self.train = train
        self.val = val
        self.rho = rho

        mnist = datasets.MNIST(root, train=train, download=True)
        self.data = mnist.data.numpy()
        self.labels = mnist.targets.numpy()

        if train and not val:
            self.data = self.data[:50000]
            self.labels = self.labels[:50000]
        elif val:
            self.data = self.data[50000:60000]
            self.labels = self.labels[50000:60000]

        self.colors = self._generate_colors()

    def _generate_colors(self) -> np.ndarray:
        """Generate color labels with spurious correlation."""
        np.random.seed(42 if self.train or self.val else 43)
        colors = np.zeros(len(self.labels), dtype=np.int64)

        for i in range(len(self.labels)):
            label = self.labels[i]

            if self.train or self.val:
                if np.random.rand() < self.rho:
                    colors[i] = 0 if label < 5 else 1
                else:
                    colors[i] = 1 if label < 5 else 0
            else:
                if np.random.rand() < self.rho:
                    colors[i] = 1 if label < 5 else 0
                else:
                    colors[i] = 0 if label < 5 else 1

        return colors

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int, int]:
        """Return (image, label, color)."""
        img = self.data[idx].astype(np.float32) / 255.0
        label = int(self.labels[idx])
        color = int(self.colors[idx])

        colored_img = np.zeros((28, 28, 3), dtype=np.float32)
        if color == 0:
            colored_img[:, :, 0] = img
        else:
            colored_img[:, :, 1] = img

        colored_img = torch.from_numpy(colored_img).permute(2, 0, 1)

        return colored_img, label, color

    def __len__(self) -> int:
        return len(self.labels)


def get_dataloaders(batch_size: int = 256, num_workers: int = 4) -> Dict[str, DataLoader]:
    """Create train/val/test dataloaders."""
    train_dataset = ColoredMNIST(root="./data", train=True, rho=0.95, val=False)
    val_dataset = ColoredMNIST(root="./data", train=True, rho=0.95, val=True)
    test_dataset = ColoredMNIST(root="./data", train=False, rho=0.95)

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=True
    )

    val_loader = DataLoader(
        val_dataset,
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
