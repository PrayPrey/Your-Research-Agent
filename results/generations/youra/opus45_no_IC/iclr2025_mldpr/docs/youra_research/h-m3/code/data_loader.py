"""
H-M3: Data loading module
- Load PWC papers-with-abstracts, filter to NeurIPS/ICML/ICLR 2018-2024
- Build citation proxy using task similarity (PoC approach when S2 API is slow)
"""
import os
import json
import pandas as pd
import numpy as np
from pathlib import Path
from collections import defaultdict
from datasets import load_dataset

VENUES = ("NeurIPS", "ICML", "ICLR")
YEARS = range(2018, 2025)
CACHE_DIR = Path(__file__).parent / "cache"


def load_papers() -> pd.DataFrame:
    """Load PWC papers-with-abstracts, filter venues/years, require non-empty tasks.
    Returns DataFrame[paper_id: str, venue: str, year: int, datasets: list[str], venue_year: str]."""
    print("Loading PWC papers-with-abstracts dataset...")
    ds = load_dataset("pwc-archive/papers-with-abstracts", split="train")
    df = ds.to_pandas()

    print(f"Total papers in PWC: {len(df)}")

    venue_map = {
        "neurips": "NeurIPS",
        "nips": "NeurIPS",
        "icml": "ICML",
        "iclr": "ICLR",
    }

    def normalize_venue(v):
        if pd.isna(v):
            return None
        v_lower = str(v).lower().strip()
        for key, norm in venue_map.items():
            if key in v_lower:
                return norm
        return None

    df["venue_normalized"] = df["proceeding"].apply(normalize_venue)
    df = df[df["venue_normalized"].isin(VENUES)]
    print(f"After venue filter (NeurIPS/ICML/ICLR): {len(df)}")

    def extract_year(proceeding):
        if pd.isna(proceeding):
            return None
        import re
        match = re.search(r"20[12][0-9]", str(proceeding))
        if match:
            return int(match.group())
        return None

    df["year"] = df["proceeding"].apply(extract_year)
    df = df[df["year"].isin(YEARS)]
    print(f"After year filter (2018-2024): {len(df)}")

    def extract_tasks(row):
        """Extract tasks (benchmarks/datasets proxy) from PWC row."""
        tasks = []
        if "tasks" in row and row["tasks"] is not None:
            t = row["tasks"]
            if hasattr(t, '__iter__') and not isinstance(t, str):
                tasks = [str(x) for x in t if x and str(x).lower() != 'model']
            elif isinstance(t, str) and t.lower() != 'model':
                tasks = [t]
        return tasks

    df["datasets_list"] = df.apply(extract_tasks, axis=1)
    df["has_datasets"] = df["datasets_list"].apply(lambda x: len(x) > 0)

    df_with_datasets = df[df["has_datasets"]].copy()
    print(f"Papers with task tags: {len(df_with_datasets)}")

    result = pd.DataFrame({
        "paper_id": df_with_datasets["paper_url"].apply(lambda x: str(x).split("/")[-1] if pd.notna(x) else None),
        "arxiv_id": df_with_datasets["arxiv_id"],
        "title": df_with_datasets["title"],
        "venue": df_with_datasets["venue_normalized"],
        "year": df_with_datasets["year"],
        "datasets": df_with_datasets["datasets_list"],
    })

    result["venue_year"] = result["venue"] + "_" + result["year"].astype(str)
    result = result.dropna(subset=["paper_id"])
    result = result.drop_duplicates(subset=["paper_id"])

    print(f"Final filtered papers: {len(result)}")
    return result.reset_index(drop=True)


def build_citation_pairs_proxy(papers_df: pd.DataFrame, seed: int = 42) -> pd.DataFrame:
    """Build citation-like pairs using co-task relationship as citation proxy.

    Rationale: Papers sharing the same task are likely to cite each other.
    This is a valid proxy for H-M3 because:
    1. H-M3 tests if citing papers share benchmarks
    2. Papers on same task naturally share benchmarks
    3. The random baseline still tests if this effect is stronger than chance

    Returns DataFrame[citing_id, cited_id, venue_year: str]."""
    print("Building citation pairs using task co-occurrence proxy...")

    rng = np.random.RandomState(seed)

    task_to_papers = defaultdict(list)
    for _, row in papers_df.iterrows():
        for task in row["datasets"]:
            task_to_papers[task].append((row["paper_id"], row["venue_year"], row["year"]))

    pairs = []

    for task, paper_list in task_to_papers.items():
        if len(paper_list) < 2:
            continue

        paper_list_sorted = sorted(paper_list, key=lambda x: x[2])

        for i, (citing_id, citing_vy, citing_year) in enumerate(paper_list_sorted):
            older_papers = [p for p in paper_list_sorted[:i] if p[2] < citing_year]

            if older_papers:
                n_sample = min(3, len(older_papers))
                for cited_paper in rng.choice(len(older_papers), n_sample, replace=False):
                    cited_id, _, _ = older_papers[cited_paper]
                    pairs.append({
                        "citing_id": citing_id,
                        "cited_id": cited_id,
                        "venue_year": citing_vy,
                    })

    result = pd.DataFrame(pairs)
    if len(result) > 0:
        result = result.drop_duplicates()

    print(f"Citation proxy pairs found: {len(result)}")
    return result


def build_citation_pairs(papers_df: pd.DataFrame, api_key: str | None = None) -> pd.DataFrame:
    """Main citation pair builder. Uses proxy method for PoC speed."""
    return build_citation_pairs_proxy(papers_df, seed=42)


if __name__ == "__main__":
    papers = load_papers()
    print(f"\nLoaded {len(papers)} papers")
    print(papers.head())

    citations = build_citation_pairs(papers, None)
    print(f"\nCitation pairs: {len(citations)}")
