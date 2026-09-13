"""H-M1: Data loading - LongBench-v2 domain-based sampling."""

import random
from datasets import load_dataset
from transformers import AutoTokenizer

from config import DOMAINS, DOMAIN_CATEGORIES, DataConfig


def load_longbench_v2():
    """Load full LongBench-v2 dataset."""
    return load_dataset("THUDM/LongBench-v2", split="train")


def sample_domain(dataset, domain: str, n: int, seed: int) -> list[str]:
    """Sample n contexts from specific domain."""
    rng = random.Random(seed)

    # Filter by domain
    domain_samples = [item for item in dataset if item.get("domain") == domain]

    # Extract context
    contexts = []
    for item in domain_samples:
        ctx = item.get("context", "")
        if ctx:
            contexts.append(ctx)

    if len(contexts) < n:
        return contexts

    return rng.sample(contexts, n)


def tokenize_probe(text: str, tokenizer: AutoTokenizer, n_tokens: int) -> dict:
    """Tokenize and truncate to first n_tokens."""
    return tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=n_tokens,
        padding=False,
    )


def load_all_samples(config: DataConfig = None) -> dict[str, list[str]]:
    """Load samples for all domains."""
    if config is None:
        config = DataConfig()

    dataset = load_longbench_v2()
    print(f"Loaded LongBench-v2: {len(dataset)} samples")

    samples_by_domain = {}
    for domain in DOMAINS:
        print(f"  Sampling {domain}...", end=" ")
        samples = sample_domain(dataset, domain, config.samples_per_domain, config.seed)
        samples_by_domain[domain] = samples
        print(f"{len(samples)} samples")

    return samples_by_domain
