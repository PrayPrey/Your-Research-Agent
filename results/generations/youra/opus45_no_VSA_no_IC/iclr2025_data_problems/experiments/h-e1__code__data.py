"""Data loading for CIFAR-10."""

import torch
from torch.utils.data import DataLoader, Subset
from torchvision import datasets, transforms
import config


def get_transform():
    return transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(config.NORMALIZE_MEAN, config.NORMALIZE_STD),
    ])


def get_loaders():
    """Returns train_loader, test_loader."""
    transform = get_transform()
    train_dataset = datasets.CIFAR10(
        root=config.DATA_DIR, train=True, download=True, transform=transform
    )
    test_dataset = datasets.CIFAR10(
        root=config.DATA_DIR, train=False, download=True, transform=transform
    )
    train_loader = DataLoader(
        train_dataset, batch_size=config.BATCH_SIZE,
        shuffle=False, num_workers=config.NUM_WORKERS, pin_memory=True
    )
    test_loader = DataLoader(
        test_dataset, batch_size=config.EVAL_BATCH_SIZE,
        shuffle=False, num_workers=config.NUM_WORKERS, pin_memory=True
    )
    return train_loader, test_loader


def get_test_subset(test_dataset, n=None):
    """Returns subset of test dataset."""
    n = n or config.EVAL_SUBSET_SIZE
    indices = list(range(min(n, len(test_dataset))))
    return Subset(test_dataset, indices)


def get_train_subset(train_dataset, n=None):
    """Returns subset of train dataset for CPU tractability."""
    n = n or getattr(config, 'TRAIN_SUBSET_SIZE', len(train_dataset))
    indices = list(range(min(n, len(train_dataset))))
    return Subset(train_dataset, indices)


def get_datasets():
    """Returns train_dataset, test_dataset."""
    transform = get_transform()
    train_dataset = datasets.CIFAR10(
        root=config.DATA_DIR, train=True, download=True, transform=transform
    )
    test_dataset = datasets.CIFAR10(
        root=config.DATA_DIR, train=False, download=True, transform=transform
    )
    return train_dataset, test_dataset
