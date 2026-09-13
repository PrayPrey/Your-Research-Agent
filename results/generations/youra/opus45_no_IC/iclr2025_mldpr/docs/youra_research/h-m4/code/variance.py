# variance.py - Benchmark breadth measurement using REAL task label data
# Instead of cross-benchmark score variance (requires actual metrics),
# we measure benchmark breadth/diversity per paper using task label counts.

import numpy as np
import pandas as pd
from config import MIN_PAPERS_PER_VY


def compute_benchmark_breadth(paper_row) -> float:
    """
    Compute benchmark breadth for a paper.

    Uses task_labels count as proxy for benchmark diversity.
    More task labels = paper evaluated on more diverse benchmarks.

    Returns count of distinct task labels (minimum 2 for multi-benchmark papers).
    """
    task_labels = paper_row.get("task_labels", [])
    if not task_labels:
        return 0

    # Count distinct task labels
    return len(set(task_labels))


def compute_breadth_concentration(paper_row) -> float:
    """
    Compute concentration index for paper's benchmark coverage.

    Higher value = more concentrated on specific benchmark types.
    Lower value = more diverse benchmark coverage.

    For H-M4: if low entropy venue-years have papers with LOWER breadth,
    that supports the hypothesis that concentration hides diversity.

    Returns: 1 / breadth (so higher = more concentrated)
    """
    breadth = compute_benchmark_breadth(paper_row)
    if breadth < 2:
        return None
    # Inverse: more breadth = lower concentration score
    return 1.0 / breadth


def aggregate_venue_year(papers_df: pd.DataFrame, min_papers: int = MIN_PAPERS_PER_VY) -> pd.DataFrame:
    """
    Compute per-paper benchmark breadth, group by (venue, year).

    Returns DataFrame with columns:
    - venue, year, mean_breadth, mean_concentration, n_papers, breadth_std
    """
    papers_df = papers_df.copy()

    # Compute breadth and concentration for each paper
    papers_df["breadth"] = papers_df.apply(compute_benchmark_breadth, axis=1)
    papers_df["concentration"] = papers_df.apply(compute_breadth_concentration, axis=1)

    # Drop papers with no valid concentration
    papers_with_metrics = papers_df.dropna(subset=["concentration"])

    aggregated = []

    for (venue, year), group in papers_with_metrics.groupby(["venue", "year"]):
        n_papers = len(group)
        if n_papers < min_papers:
            continue

        mean_breadth = group["breadth"].mean()
        mean_concentration = group["concentration"].mean()
        breadth_std = group["breadth"].std()
        paper_ids = group["paper_id"].tolist()

        aggregated.append({
            "venue": venue,
            "year": int(year),
            "mean_breadth": mean_breadth,
            "mean_concentration": mean_concentration,
            "breadth_std": breadth_std,
            "n_papers": n_papers,
            "paper_ids": paper_ids,
        })

    result = pd.DataFrame(aggregated)
    print(f"Aggregated {len(result)} venue-years from {len(papers_with_metrics)} papers")
    return result


if __name__ == "__main__":
    # Test breadth computation
    test_row = {"task_labels": ["Image Classification", "Object Detection", "Semantic Segmentation"]}
    breadth = compute_benchmark_breadth(test_row)
    concentration = compute_breadth_concentration(test_row)
    print(f"Test breadth: {breadth}, concentration: {concentration:.4f}")
