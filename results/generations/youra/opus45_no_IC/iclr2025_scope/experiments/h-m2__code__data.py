"""H-M2: Data loading - LongBench-v2 with full item preservation for accuracy scoring."""

import random
from datasets import load_dataset

from config import DOMAINS, DataConfig


def load_longbench_v2():
    """Load full LongBench-v2 dataset."""
    return load_dataset("THUDM/LongBench-v2", split="train")


def sample_domain_full(dataset, domain: str, n: int, seed: int) -> list[dict]:
    """Sample n items with context+question+answer from domain."""
    rng = random.Random(seed)

    domain_samples = [item for item in dataset if item.get("domain") == domain]

    items = []
    for item in domain_samples:
        ctx = item.get("context", "")
        if ctx:
            items.append({
                "context": ctx,
                "question": item.get("question", ""),
                "answer": item.get("answer", ""),
                "domain": domain,
            })

    if len(items) < n:
        return items

    return rng.sample(items, n)


def load_all_samples_full(config: DataConfig = None) -> list[dict]:
    """Load samples for all domains, flattened in domain-blocked order."""
    if config is None:
        config = DataConfig()

    dataset = load_longbench_v2()
    print(f"Loaded LongBench-v2: {len(dataset)} samples")

    all_samples = []
    for domain in DOMAINS:
        print(f"  Sampling {domain}...", end=" ")
        samples = sample_domain_full(dataset, domain, config.samples_per_domain, config.seed)
        all_samples.extend(samples)
        print(f"{len(samples)} samples")

    print(f"Total: {len(all_samples)} samples")
    return all_samples
