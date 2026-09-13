"""Data loading and probe pair construction for h-m1."""
import torch
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
from torchvision.datasets import CIFAR10

from config import ExperimentConfig


def get_datasets(cfg: ExperimentConfig) -> tuple:
    """CIFAR-10 train/test with ImageNet normalization for ResNet-18."""
    transform = transforms.Compose([
        transforms.Resize(224),  # ResNet-18 expects 224x224
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],  # ImageNet stats
            std=[0.229, 0.224, 0.225]
        ),
    ])
    train_ds = CIFAR10(cfg.data_root, train=True, download=True, transform=transform)
    test_ds = CIFAR10(cfg.data_root, train=False, download=True, transform=transform)
    return train_ds, test_ds


def get_loaders(train_ds: Dataset, test_ds: Dataset, cfg: ExperimentConfig) -> tuple:
    train_loader = DataLoader(
        train_ds, batch_size=cfg.batch_size, shuffle=True, num_workers=4, pin_memory=True
    )
    test_loader = DataLoader(
        test_ds, batch_size=cfg.batch_size, shuffle=False, num_workers=4, pin_memory=True
    )
    return train_loader, test_loader


def build_probe_pairs(train_ds: Dataset, test_ds: Dataset, seed: int, n_per_mode: int = 1000) -> dict:
    """Build probe pairs for 3 modes: memorization, transfer, spurious.

    Returns dict with keys 'mem', 'transfer', 'spurious', each mapping to
    list of (train_idx, test_idx) tuples.
    """
    rng = torch.Generator().manual_seed(seed)

    # Get labels
    train_labels = torch.tensor([train_ds.targets[i] for i in range(len(train_ds))])
    test_labels = torch.tensor([test_ds.targets[i] for i in range(len(test_ds))])

    probes = {}

    # Memorization: same-class pairs (proxy for near-duplicate)
    # In real scenario would do pixel distance; here use class match as proxy
    probes["mem"] = _find_memorization_pairs(train_labels, test_labels, n_per_mode, rng)

    # Feature transfer: same-class but different samples (different visual features)
    probes["transfer"] = _find_transfer_pairs(train_labels, test_labels, n_per_mode, rng)

    # Spurious: different-class pairs (no semantic relationship, only spurious features)
    probes["spurious"] = _find_spurious_pairs(train_labels, test_labels, n_per_mode, rng)

    return probes


def _find_memorization_pairs(train_labels, test_labels, n: int, rng) -> list:
    """Same-class pairs with lowest indices (proxy for most similar)."""
    pairs = []
    for c in range(10):
        train_idx = (train_labels == c).nonzero(as_tuple=True)[0]
        test_idx = (test_labels == c).nonzero(as_tuple=True)[0]
        # Take first n//10 pairs per class
        count = n // 10
        for i in range(min(count, len(train_idx), len(test_idx))):
            pairs.append((train_idx[i].item(), test_idx[i].item()))
    return pairs[:n]


def _find_transfer_pairs(train_labels, test_labels, n: int, rng) -> list:
    """Same-class pairs with random selection (different visual features)."""
    pairs = []
    for c in range(10):
        train_idx = (train_labels == c).nonzero(as_tuple=True)[0]
        test_idx = (test_labels == c).nonzero(as_tuple=True)[0]
        # Random sampling
        count = n // 10
        perm_train = torch.randperm(len(train_idx), generator=rng)[:count]
        perm_test = torch.randperm(len(test_idx), generator=rng)[:count]
        for i in range(min(count, len(perm_train), len(perm_test))):
            pairs.append((train_idx[perm_train[i]].item(), test_idx[perm_test[i]].item()))
    return pairs[:n]


def _find_spurious_pairs(train_labels, test_labels, n: int, rng) -> list:
    """Different-class pairs (proxy for spurious correlation)."""
    pairs = []
    train_perm = torch.randperm(len(train_labels), generator=rng)
    test_perm = torch.randperm(len(test_labels), generator=rng)

    for i in range(min(n * 2, len(train_perm), len(test_perm))):
        ti, tj = train_perm[i].item(), test_perm[i].item()
        if train_labels[ti] != test_labels[tj]:
            pairs.append((ti, tj))
        if len(pairs) >= n:
            break
    return pairs[:n]
