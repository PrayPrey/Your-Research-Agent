"""Data pipeline: RedPajama-v2 streaming + perplexity filter + MinHash dedup + tokenize."""

import hashlib
from typing import Iterator, Optional
import numpy as np
import torch
from datasets import load_dataset
from transformers import GPT2Tokenizer

from config import CurationConfig, DATA_CONFIG, DEDUP_MINHASH_PARAMS, TRAIN_CONFIG


def compute_percentile_threshold(
    dataset, quality_field: str, percentile: int, sample_size: int = 100_000
) -> float:
    """Compute perplexity threshold from sample."""
    values = []
    for i, example in enumerate(dataset):
        if i >= sample_size:
            break
        val = example.get(quality_field)
        if val is not None:
            values.append(val)
    if not values:
        return float("inf")
    return float(np.percentile(values, percentile))


def apply_perplexity_filter(dataset, threshold: Optional[float], quality_field: str):
    """Filter dataset by perplexity threshold."""
    if threshold is None:
        return dataset
    return dataset.filter(lambda x: x.get(quality_field, float("inf")) < threshold)


def minhash_signature(text: str, num_perm: int = 128) -> tuple:
    """Simple MinHash signature for deduplication."""
    shingles = set(text[i : i + 5] for i in range(len(text) - 4))
    if not shingles:
        return tuple([0] * num_perm)
    sigs = []
    for i in range(num_perm):
        min_hash = min(
            int(hashlib.md5(f"{s}_{i}".encode()).hexdigest(), 16) for s in shingles
        )
        sigs.append(min_hash)
    return tuple(sigs)


def jaccard_from_minhash(sig1: tuple, sig2: tuple) -> float:
    """Estimate Jaccard similarity from MinHash signatures."""
    return sum(a == b for a, b in zip(sig1, sig2)) / len(sig1)


class MinHashDeduplicator:
    """Simple streaming MinHash deduplicator."""

    def __init__(self, jaccard_threshold: float, exact: bool, num_perm: int = 128):
        self.threshold = jaccard_threshold
        self.exact = exact
        self.num_perm = num_perm
        self.seen_signatures = []
        self.seen_hashes = set()

    def is_duplicate(self, text: str) -> bool:
        if self.exact:
            text_hash = hashlib.md5(text.encode()).hexdigest()
            if text_hash in self.seen_hashes:
                return True
            self.seen_hashes.add(text_hash)
            if self.threshold >= 1.0:
                return False

        sig = minhash_signature(text, self.num_perm)
        for seen_sig in self.seen_signatures[-10000:]:  # limit memory
            if jaccard_from_minhash(sig, seen_sig) >= self.threshold:
                return True
        self.seen_signatures.append(sig)
        return False


def apply_deduplication(dataset, dedup_level: str):
    """Apply deduplication filter."""
    if dedup_level == "none":
        return dataset

    params = DEDUP_MINHASH_PARAMS[dedup_level]
    deduper = MinHashDeduplicator(
        jaccard_threshold=params["jaccard_threshold"],
        exact=params["exact"],
        num_perm=params["num_perm"],
    )

    def not_duplicate(example):
        text = example.get("raw_content", "") or example.get("text", "")
        return not deduper.is_duplicate(text)

    return dataset.filter(not_duplicate)


def tokenize_and_chunk(
    dataset, tokenizer: GPT2Tokenizer, seq_len: int = 1024
) -> Iterator[torch.Tensor]:
    """Tokenize and chunk into fixed-length sequences."""
    buffer = []
    for example in dataset:
        text = example.get("raw_content", "") or example.get("text", "")
        if not text:
            continue
        tokens = tokenizer.encode(text, add_special_tokens=False)
        buffer.extend(tokens)
        while len(buffer) >= seq_len:
            yield torch.tensor(buffer[:seq_len], dtype=torch.long)
            buffer = buffer[seq_len:]


def build_dataset(
    config: CurationConfig,
    tokenizer: Optional[GPT2Tokenizer] = None,
    max_tokens: int = None,
) -> Iterator[torch.Tensor]:
    """Build filtered, deduplicated, tokenized dataset."""
    if tokenizer is None:
        tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    if max_tokens is None:
        max_tokens = TRAIN_CONFIG["total_tokens"]
    seq_len = TRAIN_CONFIG["seq_len"]

    ds = load_dataset(
        DATA_CONFIG["dataset"],
        DATA_CONFIG["subset"],
        split=DATA_CONFIG["split"],
        streaming=DATA_CONFIG["streaming"],
        trust_remote_code=True,
    )

    threshold = None
    if config.perplexity_pct is not None:
        threshold = compute_percentile_threshold(
            ds, DATA_CONFIG["quality_field"], config.perplexity_pct
        )
        ds = load_dataset(
            DATA_CONFIG["dataset"],
            DATA_CONFIG["subset"],
            split=DATA_CONFIG["split"],
            streaming=True,
            trust_remote_code=True,
        )
        ds = apply_perplexity_filter(ds, threshold, DATA_CONFIG["quality_field"])

    ds = apply_deduplication(ds, config.dedup)

    token_count = 0
    for chunk in tokenize_and_chunk(ds, tokenizer, seq_len):
        if token_count >= max_tokens:
            break
        token_count += seq_len
        yield chunk
