"""Benchmark loaders for H-M4: TruthfulQA, HH-helpful, HH-harmless"""
from datasets import load_dataset
from config import HM4Config


def load_truthfulqa(cfg: HM4Config):
    """Load TruthfulQA MC1 dataset."""
    ds = load_dataset(cfg.truthfulqa_path, cfg.truthfulqa_subset, split="validation")
    return ds


def load_hh_helpful(cfg: HM4Config, max_samples: int = None):
    """Load HH-RLHF helpful-base test split."""
    ds = load_dataset(cfg.hh_rlhf_path, data_dir=cfg.hh_helpful_data_dir, split="test")
    if max_samples:
        ds = ds.select(range(min(max_samples, len(ds))))
    return ds


def load_hh_harmless(cfg: HM4Config, max_samples: int = None):
    """Load HH-RLHF harmless-base test split."""
    ds = load_dataset(cfg.hh_rlhf_path, data_dir=cfg.hh_harmless_data_dir, split="test")
    if max_samples:
        ds = ds.select(range(min(max_samples, len(ds))))
    return ds


def get_benchmark(name: str, cfg: HM4Config, max_samples: int = None):
    """Get benchmark by name."""
    if name == "truthfulqa":
        return load_truthfulqa(cfg)
    elif name == "hh_helpful":
        return load_hh_helpful(cfg, max_samples)
    elif name == "hh_harmless":
        return load_hh_harmless(cfg, max_samples)
    else:
        raise ValueError(f"Unknown benchmark: {name}")
