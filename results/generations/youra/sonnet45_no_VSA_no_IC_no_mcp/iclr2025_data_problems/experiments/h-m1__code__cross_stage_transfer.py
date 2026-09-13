"""
Cross-Stage Threshold Transfer for h-m1
Apply optimal pre-train thresholds to fine-tune data (and vice versa) per 03_logic.md L-2
"""
from typing import List, Dict, Tuple
from fast_curation import FastDeduplicationFilter, PerplexityFilter
import logging

logger = logging.getLogger(__name__)


def cross_apply_thresholds(
    pretrain_optimal: Tuple[float, int],
    finetune_optimal: Tuple[float, int],
    pretrain_data: List[Dict],
    finetune_data: List[Dict]
) -> Dict[str, Tuple[List[Dict], Dict]]:
    """
    Apply optimal thresholds across stages.

    Args:
        pretrain_optimal: (dedup_thresh, ppl_thresh) tuned on pretrain
        finetune_optimal: (dedup_thresh, ppl_thresh) tuned on finetune
        pretrain_data: C4 samples
        finetune_data: Dolly samples

    Returns:
        {
            "pretrain_on_pretrain": (curated, stats),
            "pretrain_on_finetune": (curated, stats),
            "finetune_on_pretrain": (curated, stats),
            "finetune_on_finetune": (curated, stats)
        }
    """
    results = {}

    # 1. Pretrain thresholds on pretrain data (optimal)
    logger.info("Applying pretrain thresholds to pretrain data (optimal)...")
    results["pretrain_on_pretrain"] = apply_thresholds(
        pretrain_data,
        pretrain_optimal[0],
        pretrain_optimal[1],
        stage_name="pretrain_on_pretrain"
    )

    # 2. Pretrain thresholds on finetune data (transfer)
    logger.info("Applying pretrain thresholds to finetune data (transfer)...")
    results["pretrain_on_finetune"] = apply_thresholds(
        finetune_data,
        pretrain_optimal[0],
        pretrain_optimal[1],
        stage_name="pretrain_on_finetune"
    )

    # 3. Finetune thresholds on pretrain data (transfer)
    logger.info("Applying finetune thresholds to pretrain data (transfer)...")
    results["finetune_on_pretrain"] = apply_thresholds(
        pretrain_data,
        finetune_optimal[0],
        finetune_optimal[1],
        stage_name="finetune_on_pretrain"
    )

    # 4. Finetune thresholds on finetune data (optimal)
    logger.info("Applying finetune thresholds to finetune data (optimal)...")
    results["finetune_on_finetune"] = apply_thresholds(
        finetune_data,
        finetune_optimal[0],
        finetune_optimal[1],
        stage_name="finetune_on_finetune"
    )

    return results


def apply_thresholds(
    data: List[Dict],
    dedup_thresh: float,
    ppl_thresh: int,
    stage_name: str
) -> Tuple[List[Dict], Dict]:
    """
    Apply single threshold config to data.

    Returns:
        (curated_samples, stats)
    """
    # Dedup (exact-match hash for PoC speed)
    dedup_filter = FastDeduplicationFilter(threshold=dedup_thresh)
    dedup_samples, dedup_stats = dedup_filter.filter_dataset(data)

    # Perplexity
    ppl_filter = PerplexityFilter(cutoff=ppl_thresh)
    curated_samples, ppl_stats = ppl_filter.filter_dataset(dedup_samples)

    stats = {
        "stage": stage_name,
        "dedup_threshold": dedup_thresh,
        "ppl_threshold": ppl_thresh,
        "original": len(data),
        "after_dedup": dedup_stats["unique"],
        "final_count": ppl_stats["passed"],
        "removed_total": len(data) - ppl_stats["passed"],
        "mean_ppl": ppl_stats["mean_ppl"],
    }

    logger.info(f"  {stage_name}: {len(data)} → {stats['final_count']} samples")
    return (curated_samples, stats)


def compute_transfer_delta(
    optimal_results: Dict,
    transferred_results: Dict,
    metrics: List[str] = ["mmlu", "hellaswag"]
) -> Dict[str, float]:
    """
    Compute performance delta per 03_logic.md L-3.

    Args:
        optimal_results: {"mmlu": 0.45, "hellaswag": 0.60}
        transferred_results: {"mmlu": 0.43, "hellaswag": 0.58}

    Returns:
        {"mmlu_delta": 0.02, "hellaswag_delta": 0.02, "max_delta": 0.02}
    """
    deltas = {}

    for metric in metrics:
        if metric not in optimal_results or metric not in transferred_results:
            logger.warning(f"Metric {metric} missing in results")
            continue

        delta = abs(optimal_results[metric] - transferred_results[metric])
        deltas[f"{metric}_delta"] = delta

    if deltas:
        deltas["max_delta"] = max(deltas.values())
    else:
        deltas["max_delta"] = 0.0

    logger.info(f"Transfer delta: {deltas}")
    return deltas
