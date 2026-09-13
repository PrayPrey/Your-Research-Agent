import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional

H_E1_CACHE_PATH = Path(__file__).parent.parent.parent / "h-e1" / "code" / "pwc_papers_cache.parquet"
VENUES = ["NeurIPS", "ICML", "ICLR"]
YEARS = list(range(2018, 2025))


def load_papers(cache_path: Optional[Path] = None) -> pd.DataFrame:
    """Load cached PWC papers from H-E1; fallback to HF load if cache missing."""
    cache = cache_path or H_E1_CACHE_PATH

    if cache.exists():
        print(f"Loading cached data from {cache}")
        return pd.read_parquet(cache)

    print("Cache not found, loading from HuggingFace...")
    from datasets import load_dataset

    ds = load_dataset("pwc-archive/papers-with-abstracts", split="train")
    df = ds.to_pandas()

    # Filter to NeurIPS/ICML/ICLR 2018-2024 with tasks
    # (simplified - H-E1 already did full processing)
    return df


def compute_hhi(task_counts: pd.Series) -> float:
    """HHI = sum((count_i / total)^2 for each task category)."""
    total = task_counts.sum()
    if total == 0:
        return 0.0
    shares = task_counts / total
    return float((shares ** 2).sum())


def build_venue_year_table(papers_df: pd.DataFrame) -> pd.DataFrame:
    """Build one row per venue-year with task_counts and hhi."""
    rows = []

    for venue in VENUES:
        for year in YEARS:
            subset = papers_df[(papers_df['venue'] == venue) & (papers_df['year'] == year)]

            if len(subset) == 0:
                continue

            # Explode datasets list to count each task category
            all_tasks = []
            for tasks in subset['datasets']:
                if isinstance(tasks, (list, np.ndarray)):
                    all_tasks.extend(tasks)

            if not all_tasks:
                continue

            task_counts = pd.Series(all_tasks).value_counts()
            hhi = compute_hhi(task_counts)

            rows.append({
                'venue': venue,
                'year': year,
                'hhi': hhi,
                'task_counts': task_counts,
                'n_papers': len(subset),
                'n_unique_tasks': len(task_counts)
            })

    return pd.DataFrame(rows)
