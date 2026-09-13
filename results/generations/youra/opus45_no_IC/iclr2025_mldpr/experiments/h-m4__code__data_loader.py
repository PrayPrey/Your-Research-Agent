# data_loader.py - PWC multi-benchmark loading + H-E1 entropy
# REAL DATA ONLY - no synthetic fallback

import pandas as pd
from pathlib import Path
from config import E1_RESULTS_PATH

# Path to cached real PWC data from H-E1
PWC_CACHE_PATH = Path(__file__).parent.parent.parent / "h-e1" / "code" / "pwc_papers_cache.parquet"


def load_entropy_by_venue_year(e1_path: str = E1_RESULTS_PATH) -> dict:
    """Load H-E1 entropy results, key by (venue, year)."""
    df = pd.read_csv(e1_path)
    return {(row["venue"], row["year"]): row["entropy"] for _, row in df.iterrows()}


def load_multi_benchmark_papers_from_pwc() -> pd.DataFrame:
    """
    Load papers that have 2+ task labels (benchmark proxies) from REAL PWC data.

    Uses cached parquet from H-E1 containing:
    - paper_id, venue, year, datasets (list of task labels)

    For H-M4, we use task label count as benchmark diversity proxy.
    Papers with more diverse task coverage = more benchmarks evaluated.

    Returns DataFrame with columns:
    - paper_id, venue, year, benchmark_count, task_labels
    """
    if not PWC_CACHE_PATH.exists():
        raise FileNotFoundError(
            f"PWC cache not found at {PWC_CACHE_PATH}. "
            "Run H-E1 first to generate the cache from real PWC data."
        )

    print(f"Loading REAL PWC data from {PWC_CACHE_PATH}")
    df = pd.read_parquet(PWC_CACHE_PATH)
    print(f"Loaded {len(df)} papers from cache")

    # Convert numpy arrays to lists and count benchmarks
    df = df.copy()
    df['task_labels'] = df['datasets'].apply(lambda x: list(x) if hasattr(x, '__iter__') else [])
    df['benchmark_count'] = df['task_labels'].apply(len)

    # Filter to papers with 2+ benchmarks (multi-benchmark requirement)
    multi_bench = df[df['benchmark_count'] >= 2].copy()
    print(f"Found {len(multi_bench)} papers with 2+ benchmark/task labels")

    if len(multi_bench) < 100:
        raise ValueError(
            f"Insufficient multi-benchmark papers ({len(multi_bench)}). "
            "Need at least 100 for statistical validity. "
            "Cannot use synthetic data - hypothesis test requires real data."
        )

    # Select columns needed for analysis
    result = multi_bench[['paper_id', 'venue', 'year', 'benchmark_count', 'task_labels']].reset_index(drop=True)

    # Venue-year coverage check
    venue_year_counts = result.groupby(['venue', 'year']).size()
    print(f"Venue-year coverage: {len(venue_year_counts)} groups")
    print(f"Papers per venue-year: min={venue_year_counts.min()}, max={venue_year_counts.max()}, median={venue_year_counts.median():.0f}")

    return result


if __name__ == "__main__":
    # Test loading
    entropy = load_entropy_by_venue_year()
    print(f"Loaded entropy for {len(entropy)} venue-years")

    papers = load_multi_benchmark_papers_from_pwc()
    print(f"Loaded {len(papers)} multi-benchmark papers")
    print(papers.head())
