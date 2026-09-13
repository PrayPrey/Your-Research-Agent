"""TruthfulQA dataset loading and splitting."""

from datasets import load_dataset
import random


def load_truthfulqa():
    """Load TruthfulQA generation split."""
    ds = load_dataset("truthful_qa", "generation", split="validation")
    return ds


def split_train_val(dataset, train_frac: float, seed: int):
    """Split dataset into train/val."""
    random.seed(seed)
    indices = list(range(len(dataset)))
    random.shuffle(indices)
    split_idx = int(len(indices) * train_frac)
    train_indices = indices[:split_idx]
    val_indices = indices[split_idx:]
    return dataset.select(train_indices), dataset.select(val_indices)
