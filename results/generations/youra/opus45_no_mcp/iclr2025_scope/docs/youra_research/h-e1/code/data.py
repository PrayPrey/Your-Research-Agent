"""Data loading and formatting for H-E1"""

from datasets import load_dataset, DatasetDict
from config import BENCHMARKS


def load_benchmark(name: str) -> DatasetDict:
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

    return dataset.map(
        tokenize_fn,
        batched=True,
        remove_columns=dataset.column_names,
    )


def get_benchmark_split(name: str) -> str:
    """Get the evaluation split for a benchmark."""
    return BENCHMARKS[name]["split"]


def get_benchmark_metric(name: str) -> str:
    """Get the metric name for a benchmark."""
    return BENCHMARKS[name]["metric"]


def get_benchmark_density(name: str) -> float:
    """Get the retrieval density for a benchmark."""
    return BENCHMARKS[name]["density"]
