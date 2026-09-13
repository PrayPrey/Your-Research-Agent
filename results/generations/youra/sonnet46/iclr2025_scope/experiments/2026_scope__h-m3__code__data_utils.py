"""Data utilities for H-M3: GLUE loading and sparsity profile loader."""
import json
import os
import re
import numpy as np
import torch
from torch.utils.data import DataLoader, Dataset
from typing import List, Optional
from transformers import AutoTokenizer


class GlueDataset(Dataset):
    def __init__(self, encodings: dict, labels: List[int]):
        self.encodings = encodings
        self.labels = labels

    def __len__(self) -> int:
        return len(self.labels)

    def __getitem__(self, idx: int) -> dict:
        item = {k: torch.tensor(v[idx]) for k, v in self.encodings.items()}
        item["labels"] = torch.tensor(self.labels[idx], dtype=torch.long)
        return item


def load_sparsity_profiles(h_m2_results_path: str) -> np.ndarray:
    """Load sparsity[layer_name→float] from h-m2/experiment_results.json["sparsity_profiles"]["0.01"].
    Returns: np.ndarray shape (32,), ordered by layer index.
    """
    with open(h_m2_results_path) as f:
        data = json.load(f)

    profiles = data["sparsity_profiles"]["0.01"]
    if isinstance(profiles, list):
        return np.array(profiles, dtype=float)

    layer_sparsity = {}
    for key, val in profiles.items():
        m = re.search(r"\.(\d+)\.", key)
        if m:
            layer_idx = int(m.group(1))
            if layer_idx not in layer_sparsity:
                layer_sparsity[layer_idx] = []
            layer_sparsity[layer_idx].append(val)

    n_layers = 32
    result = np.zeros(n_layers)
    for idx in range(n_layers):
        if idx in layer_sparsity:
            result[idx] = np.mean(layer_sparsity[idx])
    return result


def get_num_labels(task: str) -> int:
    """Returns 2 for sst2, 3 for mnli."""
    if task == "sst2":
        return 2
    elif task == "mnli":
        return 3
    else:
        raise ValueError(f"Unknown task: {task}")


def load_glue_dataloader(
    task: str,
    split: str,
    tokenizer,
    cfg,
    max_samples: Optional[int] = None,
) -> DataLoader:
    """Load GLUE SST-2 or MNLI, tokenize, return DataLoader."""
    from datasets import load_dataset

    if task == "sst2":
        dataset = load_dataset("nyu-mll/glue", "sst2", split=split)
        texts = [ex["sentence"] for ex in dataset]
        labels = [ex["label"] for ex in dataset]
        encodings = tokenizer(
            texts,
            padding="max_length",
            truncation=True,
            max_length=cfg.max_length,
            return_tensors=None,
        )
    elif task == "mnli":
        actual_split = split
        if split == "validation":
            actual_split = "validation_matched"
        dataset = load_dataset("nyu-mll/glue", "mnli", split=actual_split)
        premises = [ex["premise"] for ex in dataset]
        hypotheses = [ex["hypothesis"] for ex in dataset]
        labels = [ex["label"] for ex in dataset]
        encodings = tokenizer(
            premises,
            hypotheses,
            padding="max_length",
            truncation=True,
            max_length=cfg.max_length,
            return_tensors=None,
        )
    else:
        raise ValueError(f"Unknown task: {task}")

    if max_samples is not None:
        for k in encodings:
            encodings[k] = encodings[k][:max_samples]
        labels = labels[:max_samples]

    glue_dataset = GlueDataset(encodings, labels)
    return DataLoader(
        glue_dataset,
        batch_size=cfg.batch_size,
        shuffle=(split == "train"),
        num_workers=0,
        pin_memory=True,
    )


def _resolve_model_path(cfg) -> str:
    """Resolve HF model name to local snapshot path if cached."""
    import glob as _glob
    hf_cache = os.path.expanduser("~/.cache/huggingface/hub")
    pattern = os.path.join(hf_cache, "models--" + cfg.model_name.replace("/", "--"), "snapshots", "*")
    snapshots = _glob.glob(pattern)
    if snapshots:
        return snapshots[0]
    return cfg.model_name


def load_tokenizer(cfg):
    """Load LlamaTokenizer from local cache."""
    local_path = _resolve_model_path(cfg)
    tokenizer = AutoTokenizer.from_pretrained(
        local_path,
        local_files_only=cfg.local_files_only,
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    return tokenizer
