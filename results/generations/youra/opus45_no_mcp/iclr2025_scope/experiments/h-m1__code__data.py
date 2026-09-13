"""Data loading for H-M1: Landscape evaluation datasets"""

import torch
from torch.utils.data import DataLoader
from datasets import load_dataset
from config import BENCHMARKS, LANDSCAPE_CONFIG


def load_benchmark(name: str):
    """Load benchmark dataset from HuggingFace."""
    cfg = BENCHMARKS[name]
    if cfg["subset"]:
        ds = load_dataset(cfg["hf_id"], cfg["subset"])
    else:
        ds = load_dataset(cfg["hf_id"])
    return ds


def format_for_causal_lm(dataset, tokenizer, max_length=512):
    """Format dataset for causal language modeling."""
    def tokenize_fn(examples):
        if "question" in examples:
            texts = examples["question"]
        elif "text" in examples:
            texts = examples["text"]
        else:
            texts = [str(x) for x in examples[list(examples.keys())[0]]]

        tokenized = tokenizer(
            texts,
            truncation=True,
            max_length=max_length,
            padding="max_length",
            return_tensors=None,
        )
        tokenized["labels"] = tokenized["input_ids"].copy()
        return tokenized

    return dataset.map(tokenize_fn, batched=True, remove_columns=dataset.column_names)


def load_landscape_eval_set(name: str, tokenizer, max_length: int = 512, num_samples: int = None) -> DataLoader:
    """Load landscape evaluation dataset with batch_size=16."""
    if num_samples is None:
        num_samples = LANDSCAPE_CONFIG["eval_samples"]

    ds = load_benchmark(name)
    split = BENCHMARKS[name]["split"]
    eval_ds = ds[split].select(range(min(num_samples, len(ds[split]))))
    formatted = format_for_causal_lm(eval_ds, tokenizer, max_length)
    formatted.set_format(type="torch", columns=["input_ids", "attention_mask", "labels"])

    return DataLoader(
        formatted,
        batch_size=LANDSCAPE_CONFIG["batch_size"],
        shuffle=False,
        drop_last=True,
    )
