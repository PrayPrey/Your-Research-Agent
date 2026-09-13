"""
H-M3: Overlap computation module
- Jaccard similarity for dataset sets
- Random pair baseline sampling
- Citation vs random overlap distribution computation
"""
import random
import pandas as pd
import numpy as np
from collections import defaultdict


def jaccard_similarity(set1: set, set2: set) -> float:
    """Standard Jaccard; 0.0 if both empty."""
    if not set1 and not set2:
        return 0.0
    union = len(set1 | set2)
    return len(set1 & set2) / union if union > 0 else 0.0


def sample_random_pairs(paper_ids: list[str], n_pairs: int, seed: int = 42) -> list[tuple[str, str]]:
    """Sample n_pairs random (p1, p2) without replacement within given paper_ids scope.
    If not enough unique pairs, return what's possible."""
    rng = random.Random(seed)
    paper_list = list(paper_ids)

    if len(paper_list) < 2:
        return []

    max_possible = len(paper_list) * (len(paper_list) - 1) // 2
    n_pairs = min(n_pairs, max_possible)

    seen = set()
    pairs = []
    attempts = 0
    max_attempts = n_pairs * 10

    while len(pairs) < n_pairs and attempts < max_attempts:
        p1, p2 = rng.sample(paper_list, 2)
        key = tuple(sorted([p1, p2]))
        if key not in seen:
            seen.add(key)
            pairs.append((p1, p2))
        attempts += 1

    return pairs


def compute_citation_dataset_overlap(
    papers_df: pd.DataFrame, citations_df: pd.DataFrame, seed: int = 42
) -> tuple[list[float], list[float]]:
    """Per venue-year group: Jaccard for each citation pair + matched-N random pairs.
    Returns (citing_overlaps, random_overlaps)."""

    paper_datasets = {}
    for _, row in papers_df.iterrows():
        ds = row["datasets"]
        if isinstance(ds, list):
            paper_datasets[row["paper_id"]] = set(ds)
        else:
            paper_datasets[row["paper_id"]] = set()

    papers_by_vy = defaultdict(list)
    for _, row in papers_df.iterrows():
        papers_by_vy[row["venue_year"]].append(row["paper_id"])

    citing_overlaps = []
    random_overlaps = []

    if len(citations_df) == 0:
        print("WARNING: No citation pairs to analyze")
        return [], []

    venue_years = citations_df["venue_year"].unique()

    for vy in venue_years:
        vy_citations = citations_df[citations_df["venue_year"] == vy]
        vy_paper_ids = papers_by_vy.get(vy, [])

        if len(vy_citations) == 0 or len(vy_paper_ids) < 2:
            continue

        for _, row in vy_citations.iterrows():
            citing_ds = paper_datasets.get(row["citing_id"], set())
            cited_ds = paper_datasets.get(row["cited_id"], set())
            overlap = jaccard_similarity(citing_ds, cited_ds)
            citing_overlaps.append(overlap)

        n_citation_pairs = len(vy_citations)
        vy_seed = seed + hash(vy) % 10000
        random_pairs = sample_random_pairs(vy_paper_ids, n_citation_pairs, seed=vy_seed)

        for p1, p2 in random_pairs:
            d1 = paper_datasets.get(p1, set())
            d2 = paper_datasets.get(p2, set())
            overlap = jaccard_similarity(d1, d2)
            random_overlaps.append(overlap)

    print(f"Computed {len(citing_overlaps)} citing pair overlaps")
    print(f"Computed {len(random_overlaps)} random pair overlaps")

    return citing_overlaps, random_overlaps


if __name__ == "__main__":
    print("Testing Jaccard similarity...")
    assert jaccard_similarity(set(), set()) == 0.0
    assert jaccard_similarity({"a", "b"}, {"a", "b"}) == 1.0
    assert jaccard_similarity({"a"}, {"b"}) == 0.0
    assert abs(jaccard_similarity({"a", "b"}, {"a", "c"}) - 1/3) < 0.001
    print("All tests passed!")
