"""Dataset loading for H-E1 benchmark correlation experiment."""

from datasets import load_dataset
from config import DATASETS


def load_truthfulqa():
    """Load TruthfulQA multiple-choice dataset."""
    cfg = DATASETS["truthfulqa"]
    ds = load_dataset(cfg["path"], cfg["subset"], split=cfg["split"])
    max_samples = cfg.get("max_samples")
    if max_samples and len(ds) > max_samples:
        ds = ds.select(range(max_samples))
    return ds


def load_hhh(subset: str):
    """Load HHH dataset (helpful or harmless subset)."""
    key = f"hhh_{subset}"
    cfg = DATASETS[key]
    ds = load_dataset(cfg["path"], split=cfg["split"])
    # Filter by subset type
    filter_key = cfg.get("filter_key")
    if filter_key:
        n = len(ds)
        if filter_key == "helpful":
            ds = ds.select(range(n // 2))
        else:
            ds = ds.select(range(n // 2, n))
    # Subsample for PoC
    max_samples = cfg.get("max_samples")
    if max_samples and len(ds) > max_samples:
        ds = ds.select(range(max_samples))
    return ds
