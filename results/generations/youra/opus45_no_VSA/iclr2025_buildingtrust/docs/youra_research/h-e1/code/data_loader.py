"""Data loader for Open LLM Leaderboard results."""
import os
from pathlib import Path
import pandas as pd


def load_leaderboard(cache_path: str = "outputs/cache/open_llm_leaderboard.parquet") -> pd.DataFrame:
    """Load Open LLM Leaderboard results, using cache if available."""
    cache = Path(cache_path)
    if cache.exists():
        return pd.read_parquet(cache)
    return load_from_api_and_cache(cache_path)


def load_from_api_and_cache(cache_path: str) -> pd.DataFrame:
    """Load from HuggingFace API and cache locally."""
    from datasets import load_dataset

    ds = load_dataset("open-llm-leaderboard/contents", split="train")
    df = ds.to_pandas()

    if len(df) == 0:
        raise RuntimeError("API returned 0 rows")

    cache = Path(cache_path)
    cache.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(cache)

    return df
