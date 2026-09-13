"""
Data infrastructure for h-e1: Multi-dataset loading with spurious/core feature masking.
Supports CMNIST, Waterbirds, CelebA, NICO++ benchmarks.
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
    name: Literal['CMNIST', 'Waterbirds', 'CelebA', 'NICO++']
    batch_size: int
    num_workers: int = 4


class ColoredMNIST(Dataset):
    """CMNIST: MNIST with color bias injection."""
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


def get_dataloader(config: DatasetConfig, split: Literal['train', 'val', 'test']) -> DataLoader:
    """Load dataset with standard preprocessing."""

    if config.name == 'CMNIST':
        train_mode = (split == 'train')
        # Use 5% subset for PoC validation (reduces 60K to 3K samples)
        dataset = ColoredMNIST(root='./data/mnist', train=train_mode, subset_fraction=0.05)

        # Split train into train/val if needed
        if split == 'val':
            total = len(dataset)
            val_size = int(0.1 * total)
            _, dataset = torch.utils.data.random_split(dataset, [total - val_size, val_size])

    elif config.name == 'Waterbirds':
        try:
            from wilds import get_dataset
            dataset_obj = get_dataset(dataset='waterbirds', root_dir='./data/wilds', download=True)
            split_dict = {'train': 0, 'val': 1, 'test': 2}
            dataset = dataset_obj.get_subset(split_dict[split])
        except ImportError:
            raise RuntimeError("Waterbirds requires 'pip install wilds'")

    elif config.name == 'CelebA':
        split_map = {'train': 'train', 'val': 'valid', 'test': 'test'}
        transform = transforms.Compose([
            transforms.CenterCrop(178),
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
        dataset = datasets.CelebA(
            root='./data/celeba',
            split=split_map[split],
            target_type='attr',
            download=True,
            transform=transform
        )
        # Filter for Blond_Hair target (index 9)
        # Wrapper to extract single attribute
        class CelebABias(Dataset):
            def __init__(self, celeba):
                self.celeba = celeba
            def __len__(self):
                return len(self.celeba)
            def __getitem__(self, idx):
                img, attrs = self.celeba[idx]
                return img, attrs[9]  # Blond_Hair
        dataset = CelebABias(dataset)

    elif config.name == 'NICO++':
        raise NotImplementedError("NICO++ requires manual download from official repo")

    else:
        raise ValueError(f"Unknown dataset: {config.name}")

    return DataLoader(
        dataset,
        batch_size=config.batch_size,
        shuffle=(split == 'train'),
        num_workers=config.num_workers,
        pin_memory=True
    )


def apply_spurious_mask(images: torch.Tensor, dataset_name: str) -> torch.Tensor:
    """
    Isolate spurious feature by masking core feature.

    CMNIST: Gaussian blur to destroy shape, preserve color
    Waterbirds: Foreground mask (requires segmentation - simplified here)
    CelebA: Face region mask (gender-preserving)
    NICO++: Object mask (requires segmentation)
    """
    if dataset_name == 'CMNIST':
        # Gaussian blur with large kernel to destroy digit shape
        blurred = TF.gaussian_blur(images, kernel_size=15)
        return blurred

    elif dataset_name == 'Waterbirds':
        # Simplified: center crop to approximate background isolation
        # Real impl needs segmentation model
        h, w = images.shape[-2:]
        center_h, center_w = h // 2, w // 2
        mask = torch.ones_like(images)
        mask[:, :, center_h-50:center_h+50, center_w-50:center_w+50] = 0
        return images * mask

    elif dataset_name == 'CelebA':
        # Simplified: outer region mask to preserve face
        h, w = images.shape[-2:]
        mask = torch.zeros_like(images)
        mask[:, :, h//4:3*h//4, w//4:3*w//4] = 1
        return images * mask

    elif dataset_name == 'NICO++':
        # Simplified: center mask for context isolation
        h, w = images.shape[-2:]
        mask = torch.ones_like(images)
        mask[:, :, h//4:3*h//4, w//4:3*w//4] = 0
        return images * mask

    else:
        raise ValueError(f"Unknown dataset: {dataset_name}")


def apply_core_mask(images: torch.Tensor, dataset_name: str) -> torch.Tensor:
    """
    Isolate core feature by masking spurious feature.

    CMNIST: Randomize color channels (preserve shape, destroy color correlation)
    Waterbirds: Background mask (isolate foreground bird)
    CelebA: Gender-invariant preprocessing (simplified)
    NICO++: Context mask (isolate object)
    """
    if dataset_name == 'CMNIST':
        # Randomize color assignment per image to destroy color-label correlation
        # while preserving shape information
        batch_size = images.shape[0]
        shuffled = images.clone()
        for i in range(batch_size):
            # Random permutation of RGB channels
            perm = torch.randperm(3)
            shuffled[i] = shuffled[i, perm]
        return shuffled

    elif dataset_name == 'Waterbirds':
        # Simplified: center region for bird (real impl needs segmentation)
        h, w = images.shape[-2:]
        center_h, center_w = h // 2, w // 2
        mask = torch.zeros_like(images)
        mask[:, :, center_h-50:center_h+50, center_w-50:center_w+50] = 1
        return images * mask

    elif dataset_name == 'CelebA':
        # Simplified: face region isolation
        h, w = images.shape[-2:]
        mask = torch.ones_like(images)
        mask[:, :, h//4:3*h//4, w//4:3*w//4] = 1
        return images * mask

    elif dataset_name == 'NICO++':
        # Simplified: center object isolation
        h, w = images.shape[-2:]
        mask = torch.zeros_like(images)
        mask[:, :, h//4:3*h//4, w//4:3*w//4] = 1
        return images * mask

    else:
        raise ValueError(f"Unknown dataset: {dataset_name}")
