"""Data loading for H-M4: 4-benchmark suite (GSM8K, MMLU, HotpotQA, NQ)"""

import torch
from torch.utils.data import DataLoader
from datasets import load_dataset

from config import BENCHMARKS, TRAIN_CONFIG


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
        texts = []

        if "question" in examples:
            raw = examples["question"]
            for q in raw:
                if isinstance(q, dict) and "text" in q:
                    texts.append(q["text"])
                elif isinstance(q, str):
                    texts.append(q)
                else:
                    texts.append(str(q))
        elif "text" in examples:
            texts = [str(x) for x in examples["text"]]
        elif "context" in examples:
            texts = [str(x) for x in examples["context"]]
        else:
            key = list(examples.keys())[0]
            for v in examples[key]:
                if isinstance(v, dict) and "text" in v:
                    texts.append(v["text"])
                elif isinstance(v, str):
                    texts.append(v)
                else:
                    texts.append(str(v))

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


def load_task_loader(name: str, tokenizer, max_length: int = 512, batch_size: int = 4, split: str = None, num_samples: int = None) -> DataLoader:
    """Load task-specific DataLoader."""
    cfg = BENCHMARKS[name]
    ds = load_benchmark(name)

    use_split = split if split else cfg["split"]
    use_samples = num_samples if num_samples else cfg["num_samples"]

    split_ds = ds[use_split]
    eval_ds = split_ds.select(range(min(use_samples, len(split_ds))))
    formatted = format_for_causal_lm(eval_ds, tokenizer, max_length)
    formatted.set_format(type="torch", columns=["input_ids", "attention_mask", "labels"])

    return DataLoader(
        formatted,
        batch_size=batch_size,
        shuffle=False,
        drop_last=True,
    )


def load_benchmark_suite(tokenizer, max_length=512, batch_size=4):
    """Load all 4 benchmarks. Returns {task_name: {'loader': DataLoader, 'density': float, 'n_samples': int}}"""
    suite = {}
    for task_name, cfg in BENCHMARKS.items():
        try:
            loader = load_task_loader(task_name, tokenizer, max_length, batch_size)
            suite[task_name] = {
                "loader": loader,
                "density": cfg["retrieval_density"],
                "n_samples": len(loader.dataset),
                "config": cfg,
            }
            print(f"  Loaded {task_name}: {len(loader.dataset)} samples, density={cfg['retrieval_density']}")
        except Exception as e:
            print(f"  Warning: Failed to load {task_name}: {e}")
            continue

    total = sum(v["n_samples"] for v in suite.values())
    print(f"Total benchmark samples: {total}")
    return suite
