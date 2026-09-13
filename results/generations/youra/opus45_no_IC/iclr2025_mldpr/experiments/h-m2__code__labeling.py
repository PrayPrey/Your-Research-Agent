"""H-M2 Labeling: Standard dataset identification and paper labeling."""

import pandas as pd
from typing import Set


def compute_standard_datasets(papers_df: pd.DataFrame, venue: str, year: int, top_n: int = 5) -> Set[str]:
    """Top-N datasets by usage count for venue in given year.

    Args:
        papers_df: DataFrame with columns [paper_id, venue, year, datasets_used]
        venue: Target venue
        year: Target year (prior year for standard computation)
        top_n: Number of top datasets to consider as "standard"

    Returns:
        Set of dataset names considered "standard" for venue in year
    """
    mask = (papers_df['venue'] == venue) & (papers_df['year'] == year)
    venue_year_papers = papers_df[mask]

    if len(venue_year_papers) == 0:
        return set()

    # Explode datasets_used lists and count
    all_datasets = []
    for ds_list in venue_year_papers['datasets_used']:
        if isinstance(ds_list, list):
            all_datasets.extend(ds_list)

    if not all_datasets:
        return set()

    dataset_counts = pd.Series(all_datasets).value_counts()
    return set(dataset_counts.head(top_n).index)


def label_papers(papers_df: pd.DataFrame, hhi_df: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    """Label papers with standard_benchmark and prior_hhi.

    For each paper:
    1. Determine "standard" benchmarks from prior year's top-N datasets
    2. Label if paper uses any standard benchmark
    3. Merge prior-year HHI (year-1)

    Args:
        papers_df: DataFrame[paper_id, venue, year, datasets_used]
        hhi_df: DataFrame[venue, year, hhi_score]
        top_n: Number of top datasets considered "standard"

    Returns:
        DataFrame[paper_id, venue, year, standard_benchmark(int), prior_hhi(float)]
    """
    # Shift HHI to represent prior year (so year N in papers gets HHI from year N-1)
    hhi_shifted = hhi_df.copy()
    hhi_shifted['year'] = hhi_shifted['year'] + 1
    hhi_shifted = hhi_shifted.rename(columns={'hhi_score': 'prior_hhi'})

    # Merge papers with prior HHI
    merged_df = papers_df.merge(hhi_shifted, on=['venue', 'year'], how='inner')
    print(f"After merging with prior HHI: {len(merged_df)} papers (dropped first year per venue)")

    # Pre-compute standard datasets for each venue-year combination
    standard_cache = {}
    for venue in papers_df['venue'].unique():
        for year in papers_df['year'].unique():
            prior_year = year - 1
            if prior_year >= papers_df['year'].min():
                standard_cache[(venue, year)] = compute_standard_datasets(
                    papers_df, venue, prior_year, top_n
                )

    # Label each paper
    def uses_standard(row):
        key = (row['venue'], row['year'])
        if key not in standard_cache:
            return 0
        standard_set = standard_cache[key]
        if not standard_set:
            return 0
        paper_datasets = set(row['datasets_used']) if isinstance(row['datasets_used'], list) else set()
        return 1 if paper_datasets & standard_set else 0

    merged_df['standard_benchmark'] = merged_df.apply(uses_standard, axis=1)

    # Report distribution
    total = len(merged_df)
    standard_count = merged_df['standard_benchmark'].sum()
    print(f"Standard benchmark adoption: {standard_count}/{total} ({100*standard_count/total:.1f}%)")

    return merged_df[['paper_id', 'venue', 'year', 'standard_benchmark', 'prior_hhi']]


if __name__ == "__main__":
    from data_loader import load_papers, load_hhi_table

    papers = load_papers()
    hhi = load_hhi_table()
    labeled = label_papers(papers, hhi)
    print(f"\nLabeled papers sample:\n{labeled.head(10)}")
    print(f"\nDescriptive stats:\n{labeled.describe()}")
