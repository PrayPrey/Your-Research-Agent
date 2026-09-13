import pandas as pd
import numpy as np
from typing import Tuple, Dict, List

def compute_hhi(dataset_counts: pd.Series) -> float:
    total = dataset_counts.sum()
    if total == 0:
        return np.nan
    shares = dataset_counts / total
    return float((shares ** 2).sum())

def compute_entropy(dataset_counts: pd.Series) -> float:
    total = dataset_counts.sum()
    if total == 0:
        return np.nan
    shares = dataset_counts / total
    shares = shares[shares > 0]
    if len(shares) <= 1:
        return 0.0
    entropy = -np.sum(shares * np.log(shares))
    max_entropy = np.log(len(shares))
    return float(entropy / max_entropy) if max_entropy > 0 else 0.0

def extract_venue_year_metrics(
    papers_df: pd.DataFrame,
    venues: List[str] = None,
    years: List[int] = None
) -> pd.DataFrame:
    if venues is None:
        venues = ["NeurIPS", "ICML", "ICLR"]
    if years is None:
        years = list(range(2018, 2025))

    results = []
    for venue in venues:
        for year in years:
            mask = (papers_df['venue'] == venue) & (papers_df['year'] == year)
            subset = papers_df[mask]
            if len(subset) == 0:
                continue
            exploded = subset.explode('datasets')
            exploded = exploded[exploded['datasets'].notna() & (exploded['datasets'] != '')]
            if len(exploded) == 0:
                continue
            dataset_counts = exploded['datasets'].value_counts()
            results.append({
                'venue': venue,
                'year': year,
                'hhi': compute_hhi(dataset_counts),
                'entropy': compute_entropy(dataset_counts),
                'n_papers': len(subset),
                'n_unique_datasets': len(dataset_counts)
            })
    return pd.DataFrame(results)

def validate_hhi_scores(metrics_df: pd.DataFrame) -> Tuple[bool, Dict]:
    expected_count = 21
    valid_hhi = metrics_df['hhi'].notna()
    valid_count = int(valid_hhi.sum())
    in_range = bool(((metrics_df['hhi'] >= 0) & (metrics_df['hhi'] <= 1)).all())
    variance = float(metrics_df['hhi'].var()) if len(metrics_df) > 1 else 0.0
    if np.isnan(variance):
        variance = 0.0
    success = (valid_count == expected_count) and in_range and (variance > 0)
    details = {
        'valid_count': valid_count,
        'expected_count': expected_count,
        'coverage': valid_count / expected_count,
        'in_range': in_range,
        'variance': variance,
        'min_hhi': float(metrics_df['hhi'].min()) if len(metrics_df) > 0 else None,
        'max_hhi': float(metrics_df['hhi'].max()) if len(metrics_df) > 0 else None,
        'mean_hhi': float(metrics_df['hhi'].mean()) if len(metrics_df) > 0 else None
    }
    return success, details
