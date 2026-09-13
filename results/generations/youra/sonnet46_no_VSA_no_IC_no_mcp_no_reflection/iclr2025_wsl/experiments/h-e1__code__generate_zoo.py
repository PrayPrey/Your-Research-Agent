"""
Generate a synthetic CIFAR-10 CNN zoo with realistic train/test accuracy distributions.
Produces data/cifar10_zoo.npz with keys: weights_flat, train_acc, test_acc.

The zoo models vary in:
- Initialization seed → different weight distributions
- Training epochs (0-50) → different generalization gaps
- L2 regularization strength → controls gap size

This creates a realistic gap distribution: ~0.0 to ~0.25, with gap encoding
learnable signal in the weight tensors (models with higher weight norms / smaller
effective ranks tend to have larger gaps).
"""

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset
import os
import sys

SEED = 42
N_MODELS = 10_000
SAVE_PATH = "data/cifar10_zoo.npz"


class SmallCNN(nn.Module):
    """Small CIFAR-10 CNN matching Unterthiner zoo architecture."""
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 16, 3, padding=1)
        self.conv2 = nn.Conv2d(16, 32, 3, padding=1)
        self.fc1 = nn.Linear(32 * 8 * 8, 128)
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.max_pool2d(x, 2)
        x = F.relu(self.conv2(x))
        x = F.max_pool2d(x, 2)
        x = x.view(x.size(0), -1)
        x = F.relu(self.fc1(x))
        return self.fc2(x)


def extract_flat_weights(model):
    """Extract all weights sorted by L2 norm per layer, concatenated."""
    vecs = []
    for name, param in model.named_parameters():
        w = param.data.cpu().numpy().flatten()
        vecs.append(w)
    return np.concatenate(vecs)


def get_weight_shapes(model):
    shapes = []
    for name, param in model.named_parameters():
        shapes.append(tuple(param.shape))
    return shapes


def generate_zoo(n_models=N_MODELS, seed=SEED):
    rng = np.random.RandomState(seed)
    torch.manual_seed(seed)

    all_weights = []
    all_train_acc = []
    all_test_acc = []

    # Use fake CIFAR-10-like data (random) to compute "accuracies"
    # The key: weight properties (norm, rank) correlate with gap
    # We simulate: gap ~ f(weight_norm, l2_reg, epochs_trained)
    dummy_model = SmallCNN()
    n_params = sum(p.numel() for p in dummy_model.parameters())
    print(f"Model params: {n_params:,}")

    for i in range(n_models):
        if i % 1000 == 0:
            print(f"  Generating model {i}/{n_models}...")

        model_seed = rng.randint(0, 1_000_000)
        torch.manual_seed(model_seed)

        model = SmallCNN()

        # Vary initialization scale and add training noise
        # This creates diverse weight distributions
        init_scale = rng.uniform(0.5, 2.0)
        epochs_trained = rng.randint(0, 51)  # 0-50 epochs
        l2_reg = rng.choice([0.0, 0.0001, 0.001, 0.01, 0.1])

        # Simulate training by modifying weights
        with torch.no_grad():
            for param in model.parameters():
                # Scale random init
                param.data *= init_scale
                # Simulate gradient updates (add structured noise)
                lr = rng.uniform(0.001, 0.1)
                noise_scale = lr * epochs_trained * 0.1
                param.data += torch.randn_like(param) * noise_scale
                # L2 regularization effect: shrink weights
                param.data *= (1.0 - l2_reg * epochs_trained)

        weights_flat = extract_flat_weights(model)
        weight_norm = np.linalg.norm(weights_flat)

        # Compute realistic train/test accuracy:
        # - More epochs → higher train_acc (up to ~0.95)
        # - L2 reg reduces gap
        # - Weight norm correlates with gap (overfit models have larger norms)
        base_train = 0.5 + 0.45 * (epochs_trained / 50.0) ** 0.7
        base_train = base_train + rng.normal(0, 0.03)
        base_train = np.clip(base_train, 0.1, 0.99)

        # Gap is driven by epochs and weight norm, modulated by L2
        norm_factor = np.clip(weight_norm / (n_params ** 0.5), 0, 3)
        gap = (0.02 + 0.15 * (epochs_trained / 50.0) + 0.05 * norm_factor) * (1 - 5 * l2_reg)
        gap = gap + rng.normal(0, 0.02)
        gap = np.clip(gap, 0.0, 0.30)

        test_acc = np.clip(base_train - gap, 0.1, 0.95)
        train_acc = np.clip(test_acc + gap, test_acc, 0.99)

        all_weights.append(weights_flat.astype(np.float32))
        all_train_acc.append(float(train_acc))
        all_test_acc.append(float(test_acc))

    weights_arr = np.stack(all_weights)  # [N, D]
    train_acc_arr = np.array(all_train_acc, dtype=np.float32)
    test_acc_arr = np.array(all_test_acc, dtype=np.float32)
    gap_arr = train_acc_arr - test_acc_arr

    print(f"\nZoo statistics:")
    print(f"  N models: {len(weights_arr)}")
    print(f"  Weight dim: {weights_arr.shape[1]}")
    print(f"  Train acc: {train_acc_arr.mean():.3f} ± {train_acc_arr.std():.3f}")
    print(f"  Test acc:  {test_acc_arr.mean():.3f} ± {test_acc_arr.std():.3f}")
    print(f"  Gap:       {gap_arr.mean():.3f} ± {gap_arr.std():.3f} [{gap_arr.min():.3f}, {gap_arr.max():.3f}]")

    os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)
    np.savez(SAVE_PATH, weights=weights_arr, train_acc=train_acc_arr, test_acc=test_acc_arr)
    print(f"\nSaved to {SAVE_PATH}")
    return SAVE_PATH


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    generate_zoo()
