"""H-E1 Data Pipeline - Dataset loading and preprocessing"""
import random
from typing import Dict, List, Tuple
import random
from datasets import load_dataset
from sklearn.model_selection import train_test_split
from config import Config


def stream_instructions(cfg: Config) -> Tuple[List[Dict], List[str]]:
    """Stream FLAN dataset, discover task families, return samples + families."""
    from itertools import islice
    from collections import Counter

    print(f"Loading {cfg.dataset_name} (streaming, limit 100K scan)...")
    ds = load_dataset(cfg.dataset_name, split="train", streaming=True)

    raw_samples = []
    for item in islice(ds, 100000):
        task_name = item.get("_task_name", "unknown")
        prefix = extract_prefix(item.get("inputs", ""), cfg.prefix_chars)
        if len(prefix.strip()) < 20:
            continue
        raw_samples.append({"text": prefix, "task_family": task_name})

    # Discover frequent task families
    family_counts = Counter(s["task_family"] for s in raw_samples)
    frequent_families = [f for f, c in family_counts.most_common(20) if c >= cfg.min_samples_per_class]

    print(f"Found {len(frequent_families)} task families with ≥{cfg.min_samples_per_class} samples")

    # Filter to frequent families and balance
    filtered = [s for s in raw_samples if s["task_family"] in frequent_families]
    random.shuffle(filtered)

    # Cap per family
    per_family = {}
    samples = []
    max_per_family = cfg.n_samples // len(frequent_families) + 50
    for s in filtered:
        fam = s["task_family"]
        if per_family.get(fam, 0) < max_per_family:
            samples.append(s)
            per_family[fam] = per_family.get(fam, 0) + 1
        if len(samples) >= cfg.n_samples:
            break

    final_counts = Counter(s["task_family"] for s in samples)
    print(f"Collected {len(samples)} samples from {len(final_counts)} families")
    print(f"  Distribution: {dict(final_counts)}")
    return samples, frequent_families


def extract_prefix(text: str, max_chars: int) -> str:
    """Extract instruction prefix (first max_chars characters)."""
    text = text.strip()
    if len(text) <= max_chars:
        return text
    cutoff = text.rfind(" ", 0, max_chars)
    if cutoff == -1:
        cutoff = max_chars
    return text[:cutoff]


def encode_labels(samples: List[Dict], task_families: List[str]) -> List[int]:
    """Convert task family strings to integer labels."""
    family_to_idx = {f: i for i, f in enumerate(task_families)}
    return [family_to_idx[s["task_family"]] for s in samples]


def stratified_split(
    samples: List[Dict], labels: List[int], cfg: Config
) -> Dict[str, Tuple[List[str], List[int]]]:
    """Split samples into train/val/test by stratified sampling on labels."""
    texts = [s["text"] for s in samples]

    train_ratio, val_ratio, test_ratio = cfg.train_val_test_split

    # First split: train vs (val+test)
    X_train, X_temp, y_train, y_temp = train_test_split(
        texts, labels,
        test_size=(val_ratio + test_ratio),
        stratify=labels,
        random_state=cfg.random_state
    )

    # Second split: val vs test
    val_of_temp = val_ratio / (val_ratio + test_ratio)
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp,
        test_size=(1 - val_of_temp),
        stratify=y_temp,
        random_state=cfg.random_state
    )

    print(f"Split: train={len(X_train)}, val={len(X_val)}, test={len(X_test)}")
    return {
        "train": (X_train, y_train),
        "val": (X_val, y_val),
        "test": (X_test, y_test),
    }
