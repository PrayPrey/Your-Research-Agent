"""H-M2: Jaccard similarity computation module."""
from __future__ import annotations

import itertools
import logging
from typing import Union

logger = logging.getLogger(__name__)

COMBINED_TOTAL: int = 542


def jaccard_similarity(set_a: set, set_b: set) -> float:
    """Compute Jaccard similarity: |A ∩ B| / |A ∪ B|.

    Returns 0.0 if both sets are empty.
    """
    union = set_a | set_b
    if not union:
        return 0.0
    intersection = set_a & set_b
    return len(intersection) / len(union)


def compute_cross_model_jaccard(
    tiers: dict[str, dict[str, set]],
    tier_name: str = "hard",
) -> dict[tuple[str, str], float]:
    """Compute Jaccard similarity for all 3 model pairs on the specified tier.

    Returns:
        {(model_a, model_b): float} — exactly 3 entries for 3 models.
        Pairs use sorted model IDs for deterministic ordering.
    """
    model_ids = sorted(tiers.keys())
    results: dict[tuple[str, str], float] = {}

    for (a, b) in itertools.combinations(model_ids, 2):
        set_a = tiers[a].get(tier_name, set())
        set_b = tiers[b].get(tier_name, set())
        j = jaccard_similarity(set_a, set_b)
        results[(a, b)] = j
        logger.debug("Jaccard %s/%s: %.4f", a.split("/")[-1], b.split("/")[-1], j)

    return results


def compute_per_benchmark_jaccard(
    per_benchmark_tiers: dict[str, dict[str, dict[str, set]]],
    tier_name: str = "hard",
) -> dict[str, dict[tuple[str, str], float]]:
    """Compute per-benchmark Jaccard for all model pairs.

    Returns:
        {"humaneval": {(a, b): float}, "mbpp": {(a, b): float}}
    """
    benchmarks = ["humaneval", "mbpp"]
    result: dict[str, dict[tuple[str, str], float]] = {b: {} for b in benchmarks}

    for bench in benchmarks:
        # Build per-benchmark tiers view
        bench_tiers: dict[str, dict[str, set]] = {
            model_id: per_benchmark_tiers[model_id][bench]
            for model_id in per_benchmark_tiers
        }
        result[bench] = compute_cross_model_jaccard(bench_tiers, tier_name=tier_name)

    return result


def compute_overlap_matrix(
    tiers: dict[str, dict[str, set]],
    tier_name: str = "hard",
) -> dict[tuple[str, str], dict[str, Union[int, float]]]:
    """Compute intersection/union counts and Jaccard for all pairs.

    Returns:
        {(a, b): {"n_intersection": int, "n_union": int, "jaccard": float}}
    """
    model_ids = sorted(tiers.keys())
    result: dict[tuple[str, str], dict] = {}

    for (a, b) in itertools.combinations(model_ids, 2):
        set_a = tiers[a].get(tier_name, set())
        set_b = tiers[b].get(tier_name, set())
        intersection = set_a & set_b
        union = set_a | set_b
        j = jaccard_similarity(set_a, set_b)
        result[(a, b)] = {
            "n_intersection": len(intersection),
            "n_union": len(union),
            "jaccard": j,
        }

    return result


def compute_consensus_set(
    tiers: dict[str, dict[str, set]],
    tier_name: str = "hard",
) -> dict[str, object]:
    """Compute consensus set: problems in the specified tier for ALL models.

    Returns:
        {"task_ids": set[str], "n": int, "percentage": float}
        percentage = n / COMBINED_TOTAL (542)
    """
    model_ids = list(tiers.keys())
    if not model_ids:
        return {"task_ids": set(), "n": 0, "percentage": 0.0}

    consensus_set: set[str] = tiers[model_ids[0]].get(tier_name, set()).copy()
    for model_id in model_ids[1:]:
        consensus_set &= tiers[model_id].get(tier_name, set())

    n = len(consensus_set)
    percentage = n / COMBINED_TOTAL

    logger.info("Consensus %s set: n=%d (%.1f%%)", tier_name, n, percentage * 100)
    return {"task_ids": consensus_set, "n": n, "percentage": percentage}


def compute_overlap_counts_by_n_models(
    tiers: dict[str, dict[str, set]],
    tier_name: str = "hard",
    total_problems: int = COMBINED_TOTAL,
) -> dict[int, int]:
    """Count problems that are in the specified tier for exactly n models.

    Returns:
        {1: count, 2: count, 3: count}
    """
    model_ids = list(tiers.keys())
    n_models_total = len(model_ids)

    # Gather all task_ids across all models for the tier
    all_task_ids: set[str] = set()
    for model_id in model_ids:
        all_task_ids |= tiers[model_id].get(tier_name, set())

    counts: dict[int, int] = {n: 0 for n in range(1, n_models_total + 1)}

    for task_id in all_task_ids:
        n_in_tier = sum(
            1 for model_id in model_ids
            if task_id in tiers[model_id].get(tier_name, set())
        )
        if 1 <= n_in_tier <= n_models_total:
            counts[n_in_tier] += 1

    return counts
