"""Cross-benchmark threshold transfer evaluation for H-M3."""

from typing import List, Dict, Tuple
from calibration import calibrate_threshold, evaluate_transfer, compute_auroc_degradation
from config import TARGET_FPR, WITHIN_CLUSTER_PAIRS


def run_pair_transfer(source: str, target: str, entropy_cache: dict) -> dict:
    """Run transfer from source to target benchmark.

    entropy_cache[name] = (calib_e, calib_l, eval_e, eval_l)
    """
    src_calib_e, src_calib_l, src_eval_e, src_eval_l = entropy_cache[source]
    _, _, tgt_eval_e, tgt_eval_l = entropy_cache[target]

    threshold = calibrate_threshold(src_calib_e, src_calib_l, TARGET_FPR)
    source_result = evaluate_transfer(threshold, src_eval_e, src_eval_l)
    target_result = evaluate_transfer(threshold, tgt_eval_e, tgt_eval_l)
    degradation = compute_auroc_degradation(source_result["auroc"], target_result["auroc"])

    return {
        "source": source,
        "target": target,
        "source_auroc": source_result["auroc"],
        "target_auroc": target_result["auroc"],
        "degradation": degradation,
        "source_threshold": threshold
    }


def run_all_transfers(pairs: List[Tuple[str, str]], entropy_cache: dict) -> List[dict]:
    """Run both directions for each pair."""
    results = []
    for a, b in pairs:
        results.append(run_pair_transfer(a, b, entropy_cache))
        results.append(run_pair_transfer(b, a, entropy_cache))
    return results
