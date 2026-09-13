"""H-M2: Gate evaluation and mechanism verification."""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from h_m2.stratify import MIN_TIER_SIZE, MODEL_SHORT_NAMES, COMBINED_TOTAL

logger = logging.getLogger(__name__)

JACCARD_GATE_THRESHOLD: float = 0.3
GATE_TYPE: str = "SHOULD_WORK"


def evaluate_gate(
    jaccard_results: dict[tuple[str, str], float],
) -> tuple[bool, dict]:
    """SHOULD_WORK gate: any pair Jaccard STRICTLY > 0.3.

    Returns:
        (gate_pass: bool, gate_detail: dict)
    """
    passing_pairs: list[dict] = []
    all_pairs: list[dict] = []

    for (a, b), j in jaccard_results.items():
        short_a = MODEL_SHORT_NAMES.get(a, a)
        short_b = MODEL_SHORT_NAMES.get(b, b)
        pair_info = {
            "pair": f"{short_a} vs {short_b}",
            "model_a": a,
            "model_b": b,
            "jaccard": j,
            "passes": j > JACCARD_GATE_THRESHOLD,  # STRICT greater-than
        }
        all_pairs.append(pair_info)
        if pair_info["passes"]:
            passing_pairs.append(pair_info)

    gate_pass = len(passing_pairs) > 0
    max_jaccard = max(jaccard_results.values()) if jaccard_results else 0.0

    gate_detail = {
        "gate_type": GATE_TYPE,
        "threshold": JACCARD_GATE_THRESHOLD,
        "comparison": "strict_greater_than",
        "max_jaccard": max_jaccard,
        "results": {
            f"{MODEL_SHORT_NAMES.get(a, a)}_vs_{MODEL_SHORT_NAMES.get(b, b)}": j
            for (a, b), j in jaccard_results.items()
        },
        "all_pairs": all_pairs,
        "passing_pairs": passing_pairs,
        "passing_pairs_count": len(passing_pairs),
        "gate_satisfied": gate_pass,
    }

    logger.info(
        "Gate evaluation: %s (max_jaccard=%.4f, passing_pairs=%d/%d)",
        "PASS" if gate_pass else "FAIL",
        max_jaccard,
        len(passing_pairs),
        len(all_pairs),
    )

    return gate_pass, gate_detail


def verify_mechanism_activated(
    tiers: dict[str, dict[str, set]],
    jaccard_results: dict[tuple[str, str], float],
) -> tuple[bool, dict]:
    """Check 4 mechanism activation indicators.

    Indicators:
        tiers_populated: All 3 models have non-empty hard/easy tiers
        jaccard_computed: Exactly 3 pairs computed
        jaccard_non_trivial: At least one pair has Jaccard > 0.0
        tier_sizes_valid: All models have n_hard >= MIN_TIER_SIZE

    Returns:
        (all_activated: bool, indicators: dict)
    """
    # 1. Tiers populated
    tiers_populated = (
        len(tiers) >= 3
        and all(
            len(tiers[m].get("hard", set())) > 0
            for m in tiers
        )
    )

    # 2. Jaccard computed (exactly 3 pairs for 3 models)
    jaccard_computed = len(jaccard_results) == 3

    # 3. Jaccard non-trivial
    jaccard_non_trivial = any(j > 0.0 for j in jaccard_results.values())

    # 4. Tier sizes valid
    tier_sizes_valid = all(
        len(tiers[m].get("hard", set())) >= MIN_TIER_SIZE
        for m in tiers
    )

    all_activated = (
        tiers_populated
        and jaccard_computed
        and jaccard_non_trivial
        and tier_sizes_valid
    )

    indicators = {
        "tiers_populated": tiers_populated,
        "jaccard_computed": jaccard_computed,
        "jaccard_non_trivial": jaccard_non_trivial,
        "tier_sizes_valid": tier_sizes_valid,
        "all_activated": all_activated,
    }

    logger.info("Mechanism indicators: %s", indicators)
    return all_activated, indicators


def build_stratification_results(
    pass_at_1_data: dict[str, dict[str, float]],
    tiers: dict[str, dict[str, set]],
    per_benchmark_tiers: dict,
    jaccard_results: dict[tuple[str, str], float],
    per_benchmark_jaccard: dict,
    consensus: dict,
    gate_detail: dict,
    mechanism_indicators: dict,
) -> dict:
    """Assemble full stratification_results.json payload."""
    timestamp = datetime.now(timezone.utc).isoformat()

    # Build tier sizes summary
    tier_sizes: dict[str, dict] = {}
    for model_id, tier_sets in tiers.items():
        short = MODEL_SHORT_NAMES.get(model_id, model_id)
        tier_sizes[short] = {
            "model_id": model_id,
            "combined": {
                "n_hard": len(tier_sets["hard"]),
                "n_easy": len(tier_sets["easy"]),
                "n_medium": len(tier_sets["medium"]),
                "total": len(tier_sets["hard"]) + len(tier_sets["easy"]) + len(tier_sets["medium"]),
            },
        }
        # Per-benchmark
        if model_id in per_benchmark_tiers:
            for bench in ["humaneval", "mbpp"]:
                bt = per_benchmark_tiers[model_id][bench]
                tier_sizes[short][bench] = {
                    "n_hard": len(bt["hard"]),
                    "n_easy": len(bt["easy"]),
                    "n_medium": len(bt["medium"]),
                }

    # Jaccard results as serializable dicts
    def jaccard_dict_to_serializable(jd: dict) -> dict:
        return {
            f"{MODEL_SHORT_NAMES.get(a, a)}_vs_{MODEL_SHORT_NAMES.get(b, b)}": v
            for (a, b), v in jd.items()
        }

    results = {
        "metadata": {
            "hypothesis": "h-m2",
            "gate_type": GATE_TYPE,
            "timestamp": timestamp,
            "n_models": len(tiers),
            "n_problems_combined": COMBINED_TOTAL,
        },
        "tier_sizes": tier_sizes,
        "jaccard_results": {
            "combined": jaccard_dict_to_serializable(jaccard_results),
            "humaneval": jaccard_dict_to_serializable(per_benchmark_jaccard.get("humaneval", {})),
            "mbpp": jaccard_dict_to_serializable(per_benchmark_jaccard.get("mbpp", {})),
        },
        "consensus_hard": {
            "n": consensus["n"],
            "percentage": consensus["percentage"],
            "task_ids": sorted(consensus["task_ids"]),
        },
        "gate": gate_detail,
        "mechanism_verification": mechanism_indicators,
    }

    return results
