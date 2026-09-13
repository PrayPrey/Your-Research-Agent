"""
Synthetic and real datasets for spurious correlation experiments.

Key design: Train set has strong spurious correlation (spurious_prob_train ~0.95).
Test set has REVERSED/weak spurious correlation (spurious_prob_test ~0.1) to expose
models that rely on shortcuts. Minority groups in train are genuinely hard.
"""
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader, Subset
from torchvision import transforms
import os


class LinearSyntheticDataset(Dataset):
    """
    Gaussian mixture classification with controlled causal/spurious features.

    The critical design:
    - Causal features: weak signal (causal_snr), necessary for correct classification
    - Spurious features: strong signal (spurious_snr >> causal_snr), correlate with label
      in training (p=spurious_prob) but NOT in the OOD test set.
    - Train has majority groups (label=spurious_attr) and minority groups (label!=spurious_attr)
    - Test has reversed correlation to expose shortcut reliance.
    """
    def __init__(self, n_samples=5000, d_causal=5, d_spurious=20,
                 causal_snr=0.5, spurious_snr=2.0, spurious_prob=0.95,
                 seed=42):
        rng = np.random.RandomState(seed)

        # Generate labels
        labels = rng.randint(0, 2, size=n_samples)

        # Group assignments: spurious attr correlates with label with prob spurious_prob
        spurious_attr = np.where(
            rng.uniform(size=n_samples) < spurious_prob,
            labels,
            1 - labels
        )

        # Causal features: weak label-dependent signal
        X_causal = rng.randn(n_samples, d_causal)
        X_causal += causal_snr * (2 * labels[:, None] - 1)

        # Spurious features: strong spurious_attr-dependent signal
        X_spurious = rng.randn(n_samples, d_spurious)
        X_spurious += spurious_snr * (2 * spurious_attr[:, None] - 1)

        self.X = np.concatenate([X_causal, X_spurious], axis=1).astype(np.float32)
        self.y = labels.astype(np.int64)
        self.spurious_attr = spurious_attr.astype(np.int64)

        # Group: (label * 2 + spurious_attr) - 4 groups
        self.groups = (2 * self.y + self.spurious_attr).astype(np.int64)

        self.d_causal = d_causal
        self.d_spurious = d_spurious
        self.causal_idx = list(range(d_causal))
        self.spurious_idx = list(range(d_causal, d_causal + d_spurious))

    def __len__(self):
        return len(self.y)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx], self.groups[idx]


class LinearSyntheticOODDataset(Dataset):
    """OOD test dataset: spurious correlation is reversed (anti-correlated)."""
    def __init__(self, n_samples=2000, d_causal=5, d_spurious=20,
                 causal_snr=0.5, spurious_snr=2.0,
                 ood_spurious_prob=0.05,  # reversed: spurious attr anti-correlates with label
                 seed=123):
        rng = np.random.RandomState(seed)

        labels = rng.randint(0, 2, size=n_samples)

        # Anti-correlated spurious attributes
        spurious_attr = np.where(
            rng.uniform(size=n_samples) < ood_spurious_prob,
            labels,
            1 - labels
        )

        X_causal = rng.randn(n_samples, d_causal)
        X_causal += causal_snr * (2 * labels[:, None] - 1)

        X_spurious = rng.randn(n_samples, d_spurious)
        X_spurious += spurious_snr * (2 * spurious_attr[:, None] - 1)

        self.X = np.concatenate([X_causal, X_spurious], axis=1).astype(np.float32)
        self.y = labels.astype(np.int64)
        self.spurious_attr = spurious_attr.astype(np.int64)
        self.groups = (2 * self.y + self.spurious_attr).astype(np.int64)
        self.d_causal = d_causal
        self.d_spurious = d_spurious
        self.causal_idx = list(range(d_causal))
        self.spurious_idx = list(range(d_causal, d_causal + d_spurious))

    def __len__(self):
        return len(self.y)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx], self.groups[idx]


class WaterbirdsSimDataset(Dataset):
    """
    Simulated Waterbirds-style dataset with image-like features.

    Critical design for challenging spurious correlation:
    - Causal: WEAK foreground signal (small center pattern, low amplitude)
    - Spurious: STRONG background texture (high amplitude, large area)
    - Train: spurious_prob=0.95 (95% of samples have spurious=label)
    - OOD test: spurious_prob reversed (5% match)
    """
    def __init__(self, n_samples=5000, img_size=28, spurious_prob=0.95,
                 causal_strength=0.8, spurious_strength=3.0, seed=42):
        rng = np.random.RandomState(seed)

        labels = rng.randint(0, 2, n_samples)
        spurious_attr = np.where(
            rng.uniform(size=n_samples) < spurious_prob,
            labels,
            1 - labels
        )

        images = []
        for i in range(n_samples):
            img = rng.randn(1, img_size, img_size) * 0.5  # noisy background

            # Causal: weak center pattern depends on label
            c = img_size // 2
            r = img_size // 8  # small radius
            if labels[i] == 0:
                # Vertical bar (weak)
                img[0, c-r:c+r, c-1:c+1] += causal_strength
            else:
                # Horizontal bar (weak)
                img[0, c-1:c+1, c-r:c+r] += causal_strength

            # Spurious: strong background quadrant depends on spurious_attr
            if spurious_attr[i] == 0:
                img[0, :img_size//2, :] += spurious_strength  # top half bright
            else:
                img[0, img_size//2:, :] += spurious_strength  # bottom half bright

            images.append(img.astype(np.float32))

        self.X = torch.FloatTensor(np.stack(images))
        self.y = torch.LongTensor(labels)
        self.spurious_attr = torch.LongTensor(spurious_attr)
        self.groups = 2 * self.y + self.spurious_attr

    def __len__(self):
        return len(self.y)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx], self.groups[idx]


class WaterbirdsSimOODDataset(Dataset):
    """OOD test: spurious correlation reversed for image dataset."""
    def __init__(self, n_samples=2000, img_size=28,
                 ood_spurious_prob=0.05,
                 causal_strength=0.8, spurious_strength=3.0, seed=123):
        rng = np.random.RandomState(seed)

        labels = rng.randint(0, 2, n_samples)
        spurious_attr = np.where(
            rng.uniform(size=n_samples) < ood_spurious_prob,
            labels,
            1 - labels
        )

        images = []
        for i in range(n_samples):
            img = rng.randn(1, img_size, img_size) * 0.5

            c = img_size // 2
            r = img_size // 8
            if labels[i] == 0:
                img[0, c-r:c+r, c-1:c+1] += causal_strength
            else:
                img[0, c-1:c+1, c-r:c+r] += causal_strength

            if spurious_attr[i] == 0:
                img[0, :img_size//2, :] += spurious_strength
            else:
                img[0, img_size//2:, :] += spurious_strength

            images.append(img.astype(np.float32))

        self.X = torch.FloatTensor(np.stack(images))
        self.y = torch.LongTensor(labels)
        self.spurious_attr = torch.LongTensor(spurious_attr)
        self.groups = 2 * self.y + self.spurious_attr

    def __len__(self):
        return len(self.y)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx], self.groups[idx]


def make_group_splits(dataset, train_frac=0.8, val_frac=0.2, seed=42):
    """Split dataset into train/val (both in-distribution)."""
    rng = np.random.RandomState(seed)
    n = len(dataset)
    idx = rng.permutation(n)

    n_train = int(n * train_frac)

    train_idx = idx[:n_train]
    val_idx = idx[n_train:]

    return Subset(dataset, train_idx), Subset(dataset, val_idx)


def get_group_counts(dataset, n_groups=4):
    """Get per-group sample counts."""
    if hasattr(dataset, 'dataset'):
        # Subset
        groups = dataset.dataset.groups[np.array(dataset.indices)]
    else:
        groups = np.array(dataset.groups)

    counts = {}
    for g in range(n_groups):
        counts[g] = int((groups == g).sum())
    return counts
