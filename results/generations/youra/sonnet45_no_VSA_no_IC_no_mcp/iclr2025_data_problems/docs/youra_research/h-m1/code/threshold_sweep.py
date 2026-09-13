"""
Threshold Sweep Controller for h-m1
Grid search over deduplication × perplexity thresholds per 03_logic.md L-1
"""
from typing import List, Tuple, Dict
from itertools import product
from fast_curation import FastDeduplicationFilter, PerplexityFilter
import logging

logger = logging.getLogger(__name__)


def generate_threshold_grid(
    dedup_range: List[float] = [0.7, 0.8, 0.9],
    ppl_range: List[int] = [500, 1000, 1500]
) -> List[Tuple[float, int]]:
    """
    Generate threshold combinations.
    Returns: [(dedup, ppl), ...] - 9 combinations
    """
    return list(product(dedup_range, ppl_range))


def apply_threshold_sweep(
    dataset: List[Dict],
    threshold_grid: List[Tuple[float, int]],
    stage: str = "pretrain"
) -> Dict[Tuple[float, int], Tuple[List[Dict], Dict]]:
    """
    Apply all threshold combinations to dataset.

    Args:
        dataset: raw samples [{"instruction": str, "input": str, "output": str}]
        threshold_grid: [(dedup_thresh, ppl_thresh), ...]
        stage: "pretrain" or "finetune" (for logging)

    Returns:
        {(dedup, ppl): (curated_samples, stats)}
    """
    results = {}

    logger.info(f"Starting threshold sweep for {stage} stage ({len(threshold_grid)} configs)")

    for dedup_thresh, ppl_thresh in threshold_grid:
        logger.info(f"  Testing: dedup={dedup_thresh}, ppl={ppl_thresh}")

        # Dedup first (exact-match hash for PoC speed)
        dedup_filter = FastDeduplicationFilter(threshold=dedup_thresh)
        dedup_samples, dedup_stats = dedup_filter.filter_dataset(dataset)

        # Perplexity second
        ppl_filter = PerplexityFilter(cutoff=ppl_thresh)
        curated_samples, ppl_stats = ppl_filter.filter_dataset(dedup_samples)

        # Combine stats
        combined_stats = {
            "original": len(dataset),
            "after_dedup": dedup_stats["unique"],
            "final_count": ppl_stats["passed"],
            "removed_total": len(dataset) - ppl_stats["passed"],
            "dedup_removed": dedup_stats["removed"],
            "ppl_removed": ppl_stats["removed"],
            "mean_ppl": ppl_stats["mean_ppl"],
        }

        results[(dedup_thresh, ppl_thresh)] = (curated_samples, combined_stats)
        logger.info(f"    Result: {len(dataset)} → {combined_stats['final_count']} samples")

    return results


def select_optimal_threshold(
    sweep_results: Dict[Tuple[float, int], Tuple[List[Dict], Dict]],
    metric: str = "sample_count"
) -> Tuple[float, int]:
    """
    Pick best (dedup_thresh, ppl_cutoff) based on metric.

    Args:
        sweep_results: Output from apply_threshold_sweep
        metric: "sample_count" (max samples retained) or "mean_ppl" (min perplexity)

    Returns:
        (optimal_dedup_thresh, optimal_ppl_thresh)
    """
    if metric == "sample_count":
        # Max samples retained
        best_config = max(
            sweep_results.items(),
            key=lambda x: x[1][1]["final_count"]
        )
    elif metric == "mean_ppl":
        # Min mean perplexity
        best_config = min(
            sweep_results.items(),
            key=lambda x: x[1][1]["mean_ppl"]
        )
    else:
        raise ValueError(f"Unknown metric: {metric}")

    optimal_thresh = best_config[0]
    logger.info(f"Optimal thresholds (by {metric}): dedup={optimal_thresh[0]}, ppl={optimal_thresh[1]}")
    logger.info(f"  Stats: {best_config[1][1]}")

    return optimal_thresh
