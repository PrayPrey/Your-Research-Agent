"""Data loading and preprocessing for H-E1 experiment."""

import random
from typing import Set, Tuple

import numpy as np
import torch
from datasets import Dataset, DatasetDict, load_dataset
from torch.utils.data import DataLoader
from transformers import PreTrainedTokenizer


def load_sst2() -> DatasetDict:
    """Load SST-2 dataset from HuggingFace."""
    return load_dataset("glue", "sst2")


def inject_label_noise(
    dataset: Dataset, rate: float = 0.05, seed: int = 42
) -> Tuple[Dataset, Set[int]]:
    """Flip rate fraction of labels. Returns (noisy_dataset, mislabeled_indices)."""
    random.seed(seed)
    np.random.seed(seed)

    n_samples = len(dataset)
    n_flip = int(n_samples * rate)
    flip_indices = set(random.sample(range(n_samples), n_flip))

    labels = dataset["label"]
    new_labels = []
    for i, label in enumerate(labels):
        if i in flip_indices:
            new_labels.append(1 - label)
        else:
            new_labels.append(label)

    noisy_dataset = dataset.remove_columns("label").add_column("label", new_labels)
    return noisy_dataset, flip_indices


def tokenize_dataset(
    dataset: Dataset, tokenizer: PreTrainedTokenizer, max_length: int = 128
) -> Dataset:
    """Tokenize dataset with given tokenizer."""
    def tokenize_fn(examples):
        return tokenizer(
            examples["sentence"],
            truncation=True,
            padding="max_length",
            max_length=max_length,
            return_tensors=None,
        )

    tokenized = dataset.map(tokenize_fn, batched=True, remove_columns=["sentence", "idx"])
    tokenized.set_format("torch", columns=["input_ids", "attention_mask", "label"])
    return tokenized


def collate_fn(batch):
    """Collate function for DataLoader."""
    input_ids = torch.stack([item["input_ids"] for item in batch])
    attention_mask = torch.stack([item["attention_mask"] for item in batch])
    labels = torch.tensor([item["label"] for item in batch])
    return {"input_ids": input_ids, "attention_mask": attention_mask, "labels": labels}


def get_loaders(
    train_ds: Dataset, val_ds: Dataset, batch_size: int = 32
) -> Tuple[DataLoader, DataLoader]:
    """Create DataLoaders for train and validation datasets."""
    train_loader = DataLoader(
        train_ds, batch_size=batch_size, shuffle=True, collate_fn=collate_fn
    )
    val_loader = DataLoader(
        val_ds, batch_size=batch_size, shuffle=False, collate_fn=collate_fn
    )
    return train_loader, val_loader
