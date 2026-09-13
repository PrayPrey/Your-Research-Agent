import os
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader, Subset
from torchvision import datasets, transforms


def get_transforms(train: bool, mean: tuple, std: tuple) -> transforms.Compose:
    if train:
        return transforms.Compose([
            transforms.RandomCrop(32, padding=4),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            transforms.Normalize(mean, std),
        ])
    return transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(mean, std),
    ])


def load_cifar10(root: str, mean: tuple, std: tuple) -> tuple:
    train_ds = datasets.CIFAR10(
        root=root, train=True, download=True,
        transform=get_transforms(True, mean, std)
    )
    test_ds = datasets.CIFAR10(
        root=root, train=False, download=True,
        transform=get_transforms(False, mean, std)
    )
    return train_ds, test_ds


def load_cinic10(root: str, mean: tuple, std: tuple) -> Dataset:
    cinic_path = os.path.join(root, "cinic-10", "test")
    return datasets.ImageFolder(
        cinic_path,
        transform=get_transforms(False, mean, std)
    )


def load_svhn(root: str, mean: tuple, std: tuple) -> tuple:
    train_ds = datasets.SVHN(
        root=root, split='train', download=True,
        transform=get_transforms(True, mean, std)
    )
    test_ds = datasets.SVHN(
        root=root, split='test', download=True,
        transform=get_transforms(False, mean, std)
    )
    extra_ds = datasets.SVHN(
        root=root, split='extra', download=True,
        transform=get_transforms(False, mean, std)
    )
    return train_ds, test_ds, extra_ds


def sample_svhn_extra(dataset: Dataset, n: int, seed: int) -> Dataset:
    rng = np.random.RandomState(seed)
    indices = rng.choice(len(dataset), size=min(n, len(dataset)), replace=False)
    return Subset(dataset, indices.tolist())


def make_loader(dataset: Dataset, batch_size: int, shuffle: bool) -> DataLoader:
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=4,
        pin_memory=True,
    )
