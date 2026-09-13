"""Rank sensitivity calculation for h-m2 hypothesis."""
import numpy as np
import pandas as pd
from scipy import stats

from config import RANKS


def compute_sensitivity(ranks: list[int], f1_scores: list[float]) -> float:
    """Compute rank sensitivity as |slope| of F1 vs log2(rank)."""
    log_ranks = np.log2(ranks)
    slope, _, _, _, _ = stats.linregress(log_ranks, f1_scores)
    return abs(slope)


def compute_all_sensitivities(
    combined_df: pd.DataFrame,
    output_csv: str | None = None,
) -> pd.DataFrame:
    """Compute sensitivities for all (model, dataset, seed) combinations.

    Args:
        combined_df: DataFrame with columns [model, rank, seed, f1_score, dataset]
        output_csv: Optional path to save results

    Returns:
        DataFrame with columns [model, dataset, seed, sensitivity]
    """
    results = []

    for (model, dataset, seed), group in combined_df.groupby(["model", "dataset", "seed"]):
        group_sorted = group.sort_values("rank")
        ranks = group_sorted["rank"].tolist()
        f1_scores = group_sorted["f1_score"].tolist()

        if len(ranks) != len(RANKS):
            continue

        sensitivity = compute_sensitivity(ranks, f1_scores)
        results.append({
            "model": model,
            "dataset": dataset,
            "seed": seed,
            "sensitivity": sensitivity,
        })

    sens_df = pd.DataFrame(results)

    if output_csv:
        sens_df.to_csv(output_csv, index=False)

    return sens_df
