"""Load and format Dolly-15k dataset for embedding."""
import yaml
from datasets import load_dataset, Dataset
from pathlib import Path
from typing import List, Dict


def load_config(config_path: str = "config/experiment_config.yaml") -> dict:
    """Load experiment config."""
    with open(config_path) as f:
        return yaml.safe_load(f)


def load_and_format_dolly(cache_dir: str = "data/dolly_15k") -> tuple[Dataset, List[str]]:
    """
    Load Dolly-15k and format for embedding.
    Returns: (dataset, texts) where texts = [instruction + context + response]
    """
    dataset = load_dataset("databricks/databricks-dolly-15k", split="train", cache_dir=cache_dir)

    assert len(dataset) == 15015, f"Expected 15015 samples, got {len(dataset)}"

    texts = [format_sample(sample) for sample in dataset]

    print(f"Loaded {len(dataset)} samples from Dolly-15k")
    print(f"Sample text (first 200 chars): {texts[0][:200]}")

    return dataset, texts


def format_sample(sample: Dict[str, str]) -> str:
    """Concatenate instruction + context + response."""
    parts = []
    if sample.get("instruction"):
        parts.append(sample["instruction"])
    if sample.get("context"):
        parts.append(sample["context"])
    if sample.get("response"):
        parts.append(sample["response"])
    return " ".join(parts)


if __name__ == "__main__":
    dataset, texts = load_and_format_dolly()
    print(f"✓ Dataset loaded: {len(texts)} formatted texts")
    print(f"✓ Avg length: {sum(len(t) for t in texts) / len(texts):.0f} chars")
