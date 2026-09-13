"""H-M2 Data Loader: PWC papers and HHI table loading.

Uses H-E1's cached PWC parquet data as source.
Task categories used as dataset proxy (same approach as H-E1).
"""

import json
import os
import re
from pathlib import Path
from typing import Optional

import pandas as pd
import numpy as np

VENUES = ("NeurIPS", "ICML", "ICLR")
YEARS = range(2018, 2025)

BASE_DIR = Path(__file__).parent.parent
HE1_DIR = BASE_DIR.parent / "h-e1"
HE1_CACHE = HE1_DIR / "code" / "pwc_papers_cache.parquet"


def load_papers(cache_path: Optional[str] = None) -> pd.DataFrame:
    """Load PWC papers from H-E1 cache.

    Returns DataFrame[paper_id, venue, year, datasets_used(list[str])].
    """
    if cache_path is None:
        cache_path = HE1_CACHE

    if not Path(cache_path).exists():
        raise FileNotFoundError(f"H-E1 cache not found: {cache_path}")

    df = pd.read_parquet(cache_path)

    # Rename 'datasets' to 'datasets_used' for consistency with H-M2 architecture
    if 'datasets' in df.columns:
        df = df.rename(columns={'datasets': 'datasets_used'})

    # Ensure datasets_used is list type
    def ensure_list(x):
        if isinstance(x, list):
            return x
        if isinstance(x, str):
            return [x]
        if isinstance(x, np.ndarray):
            return x.tolist()
        try:
            if pd.isna(x):
                return []
        except (ValueError, TypeError):
            pass
        if hasattr(x, '__iter__') and not isinstance(x, str):
            return list(x)
        return []

    df['datasets_used'] = df['datasets_used'].apply(ensure_list)

    # Filter to target venues/years
    df = df[df['venue'].isin(VENUES) & df['year'].isin(YEARS)]

    print(f"Loaded {len(df)} papers from H-E1 cache")
    print(f"Venue distribution: {df['venue'].value_counts().to_dict()}")
    print(f"Year range: {df['year'].min()} - {df['year'].max()}")

    return df


def compute_hhi(task_counts: pd.Series) -> float:
    """HHI = sum((count_i/total)^2). Reimplemented from H-M1 spec."""
    if task_counts.sum() == 0:
        return 0.0
    shares = task_counts / task_counts.sum()
    return float((shares ** 2).sum())


def load_hhi_table() -> pd.DataFrame:
    """Compute HHI per venue-year from H-E1 cache.

    Returns DataFrame[venue, year, hhi_score].
    """
    papers_df = load_papers()
    return _compute_hhi_table(papers_df)


def _compute_hhi_table(papers_df: pd.DataFrame) -> pd.DataFrame:
    """Compute HHI for each venue-year combination."""
    records = []

    for venue in VENUES:
        for year in YEARS:
            mask = (papers_df['venue'] == venue) & (papers_df['year'] == year)
            venue_year_papers = papers_df[mask]

            if len(venue_year_papers) == 0:
                continue

            # Explode datasets and count
            all_datasets = []
            for ds_list in venue_year_papers['datasets_used']:
                if isinstance(ds_list, list):
                    all_datasets.extend(ds_list)

            if not all_datasets:
                # No datasets, skip
                continue

            task_counts = pd.Series(all_datasets).value_counts()
            hhi = compute_hhi(task_counts)

            records.append({
                'venue': venue,
                'year': year,
                'hhi_score': hhi,
                'n_papers': len(venue_year_papers),
                'n_unique_datasets': len(task_counts)
            })

    df = pd.DataFrame(records)
    print(f"\nComputed HHI for {len(df)} venue-years")
    print(f"HHI range: [{df['hhi_score'].min():.4f}, {df['hhi_score'].max():.4f}]")
    print(f"HHI mean: {df['hhi_score'].mean():.4f}")

    return df


if __name__ == "__main__":
    papers = load_papers()
    print(f"\nPapers sample:\n{papers.head()}")
    print(f"\nDatasets sample (first 5):")
    for i, row in papers.head().iterrows():
        print(f"  {row['paper_id'][:50]}... -> {row['datasets_used']}")

    hhi = load_hhi_table()
    print(f"\nHHI table:\n{hhi}")
