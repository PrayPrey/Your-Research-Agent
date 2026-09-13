"""Synthetic data generator for calibration PoC.

For EXISTENCE hypothesis, we generate synthetic pairwise comparison data
that simulates the Tree-LSTM output distribution. This allows us to validate
the calibration methodology without waiting for full CodeForces dataset setup.
"""
import numpy as np
import torch
from typing import Tuple, List
import json


def generate_synthetic_pairwise_data(
    n_samples=500,
    feature_dim=10,
    seed=42
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Generate synthetic pairwise comparison data.

    Returns:
        features: [N, feature_dim] - Simulated AST features
        labels: [N] - Binary labels (0: A faster, 1: B faster)
        true_probs: [N] - Ground truth probabilities for calibration validation
    """
    np.random.seed(seed)

    # Generate feature vectors
    features = np.random.randn(n_samples, feature_dim).astype(np.float32)

    # Generate labels with controlled class balance
    labels = (np.random.rand(n_samples) > 0.5).astype(np.int64)

    # Generate true probabilities (for validation)
    # Add noise to make calibration non-trivial
    true_probs = 0.5 + 0.3 * np.random.randn(n_samples)
    true_probs = np.clip(true_probs, 0.1, 0.9)

    return features, labels, true_probs


def create_cv_splits(n_samples, n_folds=10, seed=42):
    """Create stratified cross-validation splits."""
    from sklearn.model_selection import StratifiedKFold

    # Generate dummy labels for stratification
    dummy_labels = np.array([i % 2 for i in range(n_samples)])

    skf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=seed)

    folds = []
    for train_val_idx, test_idx in skf.split(np.arange(n_samples), dummy_labels):
        # Split train_val into train and val (80/10/10)
        val_size = len(train_val_idx) // 9  # 10% of total
        train_idx = train_val_idx[val_size:]
        val_idx = train_val_idx[:val_size]

        folds.append({
            'train': train_idx.tolist(),
            'val': val_idx.tolist(),
            'test': test_idx.tolist()
        })

    return folds


def save_synthetic_dataset(output_dir='./data/codeforces', n_samples=500, seed=42):
    """Generate and save synthetic dataset."""
    import os
    os.makedirs(output_dir, exist_ok=True)

    # Generate data
    features, labels, true_probs = generate_synthetic_pairwise_data(
        n_samples=n_samples, seed=seed
    )

    # Save arrays
    np.save(f'{output_dir}/features.npy', features)
    np.save(f'{output_dir}/labels.npy', labels)
    np.save(f'{output_dir}/true_probs.npy', true_probs)

    # Generate CV folds
    folds = create_cv_splits(n_samples, n_folds=10, seed=seed)

    # Save fold indices
    with open(f'{output_dir}/cv_folds.json', 'w') as f:
        json.dump(folds, f, indent=2)

    print(f"[Data] Generated synthetic dataset:")
    print(f"  - Samples: {n_samples}")
    print(f"  - Feature dim: {features.shape[1]}")
    print(f"  - Class balance: {labels.sum()}/{len(labels)}")
    print(f"  - CV folds: 10")
    print(f"  - Output dir: {output_dir}")

    return features, labels, folds


if __name__ == '__main__':
    save_synthetic_dataset()
