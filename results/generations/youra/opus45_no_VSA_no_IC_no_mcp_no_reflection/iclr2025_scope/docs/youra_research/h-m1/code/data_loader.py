"""WikiText-103 data loading for validation."""

from typing import List, Dict
import torch
from torch import Tensor
from datasets import load_dataset
from transformers import BertTokenizer


def load_wikitext_samples(
    num_samples: int = 100,
    min_length: int = 512,
    max_length: int = 2048,
    cache_dir: str = None
) -> List[Dict[str, Tensor]]:
    """
    Load WikiText-103 validation samples.

    Returns:
        List of {"input_ids": Tensor, "attention_mask": Tensor}
    """
    dataset = load_dataset(
        "wikitext", "wikitext-103-raw-v1",
        split="validation",
        cache_dir=cache_dir
    )
    tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

    samples = []
    for item in dataset:
        text = item["text"].strip()
        if len(text) < 100:
            continue

        encoding = tokenizer(
            text,
            truncation=True,
            max_length=max_length,
            return_tensors="pt"
        )

        seq_len = encoding["input_ids"].shape[1]
        if seq_len >= min_length:
            samples.append({
                "input_ids": encoding["input_ids"],
                "attention_mask": encoding["attention_mask"]
            })

        if len(samples) >= num_samples:
            break

    return samples
