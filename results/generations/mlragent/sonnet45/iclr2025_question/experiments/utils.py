"""
Utility functions for experiments.
"""

import random
import numpy as np
import torch
import json
import os
from datetime import datetime


def set_random_seed(seed: int):
    """Set random seed for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def save_results(results: dict, filename: str, results_dir: str):
    """Save results to JSON file."""
    os.makedirs(results_dir, exist_ok=True)
    filepath = os.path.join(results_dir, filename)
    with open(filepath, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {filepath}")


def load_results(filename: str, results_dir: str) -> dict:
    """Load results from JSON file."""
    filepath = os.path.join(results_dir, filename)
    with open(filepath, 'r') as f:
        results = json.load(f)
    return results


class Logger:
    """Simple logger for experiment tracking."""

    def __init__(self, log_file: str):
        self.log_file = log_file
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

    def log(self, message: str):
        """Log a message with timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        with open(self.log_file, 'a') as f:
            f.write(log_message + '\n')


def split_dataset(dataset: list, train_ratio: float, val_ratio: float, test_ratio: float):
    """Split dataset into train, validation, and test sets."""
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6, "Ratios must sum to 1"

    n = len(dataset)
    indices = list(range(n))
    random.shuffle(indices)

    train_end = int(n * train_ratio)
    val_end = train_end + int(n * val_ratio)

    train_indices = indices[:train_end]
    val_indices = indices[train_end:val_end]
    test_indices = indices[val_end:]

    train_data = [dataset[i] for i in train_indices]
    val_data = [dataset[i] for i in val_indices]
    test_data = [dataset[i] for i in test_indices]

    return train_data, val_data, test_data
