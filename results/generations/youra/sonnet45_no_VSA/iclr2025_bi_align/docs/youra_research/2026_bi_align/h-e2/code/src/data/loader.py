"""Data loading utilities for CNN and Transformer datasets."""

import time
from typing import Union
import torch
from torch.utils.data import DataLoader, Dataset
import torchvision
import torchvision.transforms as transforms
from datasets import load_dataset
from transformers import AutoTokenizer

from config import CNNConfig, TransformerConfig


class JitterDataLoader:
    """Wrapper to inject artificial delays in data loading."""

    def __init__(self, dataloader: DataLoader, delay_ms: int):
        """
        Args:
            dataloader: Original DataLoader
            delay_ms: Delay in milliseconds to inject between batches
        """
        self.dataloader = dataloader
        self.delay_s = delay_ms / 1000.0

    def __iter__(self):
        for batch in self.dataloader:
            if self.delay_s > 0:
                time.sleep(self.delay_s)
            yield batch

    def __len__(self):
        return len(self.dataloader)


def get_cnn_dataloader(config: CNNConfig, train: bool = True, limit_batches: int = None) -> DataLoader:
    """
    Create DataLoader for CNN datasets.

    Args:
        config: CNN configuration
        train: If True, load training set; else validation set
        limit_batches: If set, limit dataset to this many batches (for profiling)

    Returns:
        DataLoader instance
    """
    # Define transforms
    if config.dataset == "cifar10":
        transform_list = [
            transforms.Resize(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ]

        if train:
            transform_list.insert(0, transforms.RandomHorizontalFlip())
            transform_list.insert(1, transforms.RandomCrop(224, padding=4))

        transform = transforms.Compose(transform_list)

        dataset = torchvision.datasets.CIFAR10(
            root='./data',
            train=train,
            download=True,
            transform=transform
        )

    elif config.dataset == "imagenet":
        # For PoC, we'll use a subset or skip ImageNet
        # Placeholder: use CIFAR-10 as fallback
        transform_list = [
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ]

        if train:
            transform_list.insert(0, transforms.RandomHorizontalFlip())
            transform_list.insert(0, transforms.RandomResizedCrop(224))

        transform = transforms.Compose(transform_list)

        # Fallback to CIFAR-10 for PoC
        dataset = torchvision.datasets.CIFAR10(
            root='./data',
            train=train,
            download=True,
            transform=transform
        )
    else:
        raise ValueError(f"Unknown CNN dataset: {config.dataset}")

    # Limit dataset size if specified
    if limit_batches is not None:
        total_samples = limit_batches * config.batch_size
        dataset = torch.utils.data.Subset(dataset, range(min(total_samples, len(dataset))))

    dataloader = DataLoader(
        dataset,
        batch_size=config.batch_size,
        shuffle=train,
        num_workers=2,
        pin_memory=True,
        persistent_workers=True
    )

    return dataloader


def get_transformer_dataloader(config: TransformerConfig, train: bool = True, limit_batches: int = None) -> DataLoader:
    """
    Create DataLoader for Transformer datasets.

    Args:
        config: Transformer configuration
        train: If True, load training set; else validation set
        limit_batches: If set, limit dataset to this many batches (for profiling)

    Returns:
        DataLoader instance
    """
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(config.model_name)

    # Add padding token if missing
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # Load dataset
    if config.dataset == "wildchat":
        # Use a smaller public conversational dataset as fallback
        hf_dataset = load_dataset("daily_dialog", split="train" if train else "validation")
        text_field = "dialog"

    elif config.dataset == "personachat":
        hf_dataset = load_dataset("bavard/personachat_truecased", split="train" if train else "validation")
        text_field = "utterances"

    else:
        raise ValueError(f"Unknown Transformer dataset: {config.dataset}")

    # Tokenize dataset
    def tokenize_function(examples):
        # Handle different dataset formats
        if text_field == "dialog":
            texts = [" ".join(dialog) for dialog in examples[text_field]]
        elif text_field == "utterances":
            # personachat format
            texts = []
            for item in examples[text_field]:
                if isinstance(item, list):
                    texts.append(" ".join([u for u in item if isinstance(u, str)]))
                else:
                    texts.append(str(item))
        else:
            texts = examples[text_field]

        return tokenizer(
            texts,
            padding="max_length",
            truncation=True,
            max_length=config.seq_length,
            return_tensors="pt"
        )

    # Tokenize and format
    tokenized_dataset = hf_dataset.map(tokenize_function, batched=True, remove_columns=hf_dataset.column_names)
    tokenized_dataset.set_format(type="torch", columns=["input_ids", "attention_mask"])

    # Limit dataset size if specified
    if limit_batches is not None:
        total_samples = limit_batches * config.batch_size
        tokenized_dataset = tokenized_dataset.select(range(min(total_samples, len(tokenized_dataset))))

    # Custom collate function for language modeling
    def collate_fn(batch):
        input_ids = torch.stack([item["input_ids"] for item in batch])
        attention_mask = torch.stack([item["attention_mask"] for item in batch])
        # Labels are the same as input_ids for language modeling
        labels = input_ids.clone()
        return (input_ids, labels)

    dataloader = DataLoader(
        tokenized_dataset,
        batch_size=config.batch_size,
        shuffle=train,
        num_workers=2,
        collate_fn=collate_fn
    )

    return dataloader


def inject_jitter_delay(dataloader: DataLoader, delay_ms: int) -> JitterDataLoader:
    """
    Wrap DataLoader with artificial delay injection.

    Args:
        dataloader: Original DataLoader
        delay_ms: Delay in milliseconds to inject between batches

    Returns:
        JitterDataLoader wrapper
    """
    return JitterDataLoader(dataloader, delay_ms)
