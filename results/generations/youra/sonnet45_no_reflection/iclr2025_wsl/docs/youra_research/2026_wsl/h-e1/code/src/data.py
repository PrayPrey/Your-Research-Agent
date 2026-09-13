"""Dataset loading and preprocessing for ModelZoo-14K"""

import os
import torch
import numpy as np
from typing import Dict, List, Tuple
from torch.utils.data import Dataset, DataLoader


class ModelZooDataset(Dataset):
    """Synthetic dataset simulating ModelZoo-14K for proof-of-concept"""

    def __init__(self, num_models: int, weight_dim: int, split: str, seed: int = 42):
        self.num_models = num_models
        self.weight_dim = weight_dim
        self.split = split

        np.random.seed(seed + hash(split) % 1000)

        # Architecture distribution
        arch_counts = {
            "CNN": int(num_models * 0.4),
            "Transformer": int(num_models * 0.4),
            "RNN": num_models - int(num_models * 0.8)
        }

        self.arch_labels = []
        self.model_ids = []

        arch_to_idx = {"CNN": 0, "Transformer": 1, "RNN": 2}

        idx = 0
        for arch, count in arch_counts.items():
            for i in range(count):
                self.arch_labels.append(arch_to_idx[arch])
                self.model_ids.append(f"{arch}_{split}_{i}")
                idx += 1

        self.arch_labels = np.array(self.arch_labels)

    def __len__(self) -> int:
        return self.num_models

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        np.random.seed(idx + hash(self.split) % 10000)

        # Generate synthetic weights with architecture-specific patterns
        arch_label = self.arch_labels[idx]

        # Different architectures have different weight distributions
        if arch_label == 0:  # CNN
            weights = np.random.randn(self.weight_dim) * 0.1 + np.sin(np.linspace(0, 10, self.weight_dim)) * 0.5
        elif arch_label == 1:  # Transformer
            weights = np.random.randn(self.weight_dim) * 0.15 + np.cos(np.linspace(0, 15, self.weight_dim)) * 0.3
        else:  # RNN
            weights = np.random.randn(self.weight_dim) * 0.12 + np.tanh(np.linspace(-5, 5, self.weight_dim)) * 0.4

        # Normalize
        weights = (weights - weights.mean()) / (weights.std() + 1e-8)

        return {
            'weights': torch.FloatTensor(weights),
            'arch_label': torch.LongTensor([arch_label])[0],
            'model_id': self.model_ids[idx]
        }


def create_dataloaders(
    weight_dim: int,
    batch_size: int,
    num_workers: int = 0,
    pin_memory: bool = False,
    seed: int = 42
) -> Tuple[DataLoader, DataLoader, DataLoader]:
    """Create train/val/test dataloaders with synthetic data"""

    # Reduced dataset sizes for proof-of-concept
    train_dataset = ModelZooDataset(num_models=1000, weight_dim=weight_dim, split="train", seed=seed)
    val_dataset = ModelZooDataset(num_models=200, weight_dim=weight_dim, split="val", seed=seed)
    test_dataset = ModelZooDataset(num_models=200, weight_dim=weight_dim, split="test", seed=seed)

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=pin_memory
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=pin_memory
    )

    test_loader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=pin_memory
    )

    return train_loader, val_loader, test_loader


def create_frozen_k_loader(
    weight_dim: int,
    batch_size: int,
    seed: int = 42
) -> DataLoader:
    """Create RNN-only test loader for frozen-K generalization"""

    class RNNOnlyDataset(Dataset):
        def __init__(self, num_models: int, weight_dim: int, seed: int):
            self.num_models = num_models
            self.weight_dim = weight_dim
            np.random.seed(seed)

        def __len__(self):
            return self.num_models

        def __getitem__(self, idx):
            np.random.seed(idx + 50000)
            weights = np.random.randn(self.weight_dim) * 0.12 + np.tanh(np.linspace(-5, 5, self.weight_dim)) * 0.4
            weights = (weights - weights.mean()) / (weights.std() + 1e-8)

            return {
                'weights': torch.FloatTensor(weights),
                'arch_label': torch.LongTensor([2])[0],  # RNN = 2
                'model_id': f"RNN_frozen_k_{idx}"
            }

    dataset = RNNOnlyDataset(num_models=100, weight_dim=weight_dim, seed=seed)
    return DataLoader(dataset, batch_size=batch_size, shuffle=False)
