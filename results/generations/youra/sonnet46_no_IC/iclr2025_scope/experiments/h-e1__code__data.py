from __future__ import annotations
import torch
from torch.utils.data import DataLoader
from config import MODEL_CONFIGS


def load_mnli(tokenizer, max_length: int = 128, batch_size: int = 32,
              max_train_samples: int = None, max_val_samples: int = None):
    """Returns (train_loader, val_matched_loader). Full MNLI splits, with optional subsampling."""
    from datasets import load_dataset

    ds = load_dataset("glue", "mnli")

    if max_train_samples:
        ds["train"] = ds["train"].shuffle(seed=42).select(range(min(max_train_samples, len(ds["train"]))))
    if max_val_samples:
        ds["validation_matched"] = ds["validation_matched"].select(range(min(max_val_samples, len(ds["validation_matched"]))))

    def tokenize(batch):
        return tokenizer(
            batch["premise"],
            batch["hypothesis"],
            truncation=True,
            padding="max_length",
            max_length=max_length,
        )

    train_ds = ds["train"].map(tokenize, batched=True, remove_columns=["premise", "hypothesis", "idx"])
    val_ds = ds["validation_matched"].map(tokenize, batched=True, remove_columns=["premise", "hypothesis", "idx"])

    train_ds = train_ds.rename_column("label", "labels")
    val_ds = val_ds.rename_column("label", "labels")
    train_ds.set_format(type="torch", columns=["input_ids", "attention_mask", "labels"])
    val_ds.set_format(type="torch", columns=["input_ids", "attention_mask", "labels"])

    # token_type_ids if available
    if "token_type_ids" in train_ds.column_names:
        train_ds.set_format(type="torch", columns=["input_ids", "attention_mask", "token_type_ids", "labels"])
        val_ds.set_format(type="torch", columns=["input_ids", "attention_mask", "token_type_ids", "labels"])

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=4, pin_memory=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size * 2, shuffle=False, num_workers=4, pin_memory=True)
    return train_loader, val_loader


def load_cifar10(batch_size: int = 128):
    """Returns (train_loader, test_loader). Full CIFAR-10 splits, 224x224 resize."""
    import torchvision.transforms as T
    import torchvision.datasets as datasets

    mean = [0.485, 0.456, 0.406]
    std = [0.229, 0.224, 0.225]

    train_transform = T.Compose([
        T.RandomHorizontalFlip(),
        T.RandomCrop(32, padding=4),
        T.Resize(224),
        T.ToTensor(),
        T.Normalize(mean, std),
    ])
    test_transform = T.Compose([
        T.Resize(224),
        T.ToTensor(),
        T.Normalize(mean, std),
    ])

    train_ds = datasets.CIFAR10(root="/tmp/cifar10", train=True, download=True, transform=train_transform)
    test_ds = datasets.CIFAR10(root="/tmp/cifar10", train=False, download=True, transform=test_transform)

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=4, pin_memory=True)
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False, num_workers=4, pin_memory=True)
    return train_loader, test_loader


def get_data_loaders(model_name: str, tokenizer_or_processor, cfg):
    """Dispatch to load_mnli or load_cifar10 based on model task."""
    task = MODEL_CONFIGS[model_name]["task"]
    if task == "cifar10":
        return load_cifar10(batch_size=cfg.batch_size_vit)
    else:
        return load_mnli(
            tokenizer_or_processor,
            max_length=cfg.max_length,
            batch_size=cfg.batch_size_nlp,
            max_train_samples=getattr(cfg, "max_train_samples", None),
            max_val_samples=getattr(cfg, "max_val_samples", None),
        )
