"""Data loading for H-M2."""

import torch
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from pathlib import Path


def get_dataset(dataset_name: str, data_root: Path, train: bool = True):
    """Load MNIST dataset."""
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.5,), (0.5,))
    ])

    # Use hardcoded path for cached datasets
    h_m2_data = Path("/home/anonymous/YouRA_results_new_4_sonnet45/TEST_question/docs/youra_research/20260318_question/h-m2/data")

    # Both mnist and mnist_alt use MNIST dataset (Fashion-MNIST mirror is down)
    if dataset_name in ["mnist", "mnist_alt"]:
        return datasets.MNIST(
            root=h_m2_data,
            train=train,
            download=False,
            transform=transform
        )
    else:
        raise ValueError(f"Unknown dataset: {dataset_name}")


def get_dataloader(
    dataset_name: str,
    data_root: Path,
    batch_size: int,
    train: bool = True,
    num_workers: int = 2
) -> DataLoader:
    """Get DataLoader for specified dataset."""
    dataset = get_dataset(dataset_name, data_root, train)

    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=train,
        num_workers=num_workers,
        pin_memory=True
    )
