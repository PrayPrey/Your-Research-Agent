import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
from sklearn.metrics import roc_auc_score

from config import ExperimentConfig


def compute_auroc(labels: List[int], scores: List[float]) -> float:
    """Compute AUROC. labels: binary ints, scores: float (higher = more hallucinated)."""
    return float(roc_auc_score(labels, scores))


def bootstrap_auroc_ci(
    labels: List[int],
    scores: List[float],
    n_resamples: int = 1000,
    seed: int = 42,
) -> Tuple[float, float]:
    """Return (lower_95ci, upper_95ci) from bootstrap resampling."""
    rng = np.random.default_rng(seed)
    labels_arr = np.array(labels)
    scores_arr = np.array(scores)
    n = len(labels_arr)
    boot_aurocs = []
    for _ in range(n_resamples):
        idx = rng.integers(0, n, size=n)
        lbl = labels_arr[idx]
        scr = scores_arr[idx]
        if len(np.unique(lbl)) < 2:
            continue
        boot_aurocs.append(float(roc_auc_score(lbl, scr)))
    if not boot_aurocs:
        point = float(roc_auc_score(labels_arr, scores_arr))
        return point, point
    lower = float(np.percentile(boot_aurocs, 2.5))
    upper = float(np.percentile(boot_aurocs, 97.5))
    return lower, upper


def pairwise_auroc_differences(
    auroc_map: Dict[str, float],
    ci_map: Dict[str, Tuple[float, float]],
) -> List[Dict[str, Any]]:
    """All pairwise AUROC comparisons between methods."""
    methods = sorted(auroc_map.keys())
    results = []
    for i in range(len(methods)):
        for j in range(i + 1, len(methods)):
            m1, m2 = methods[i], methods[j]
            auroc1, auroc2 = auroc_map[m1], auroc_map[m2]
            ci1, ci2 = ci_map[m1], ci_map[m2]

            # Winner = higher AUROC
            if auroc1 >= auroc2:
                winner, loser = m1, m2
                delta = auroc1 - auroc2
                ci_lower_winner, ci_upper_winner = ci1
                ci_lower_loser, ci_upper_loser = ci2
            else:
                winner, loser = m2, m1
                delta = auroc2 - auroc1
                ci_lower_winner, ci_upper_winner = ci2
                ci_lower_loser, ci_upper_loser = ci1

            # Non-overlapping CIs: winner's lower bound > loser's upper bound
            ci_non_overlapping = ci_lower_winner > ci_upper_loser

            results.append({
                "method_a": m1,
                "method_b": m2,
                "winner": winner,
                "loser": loser,
                "auroc_winner": auroc_map[winner],
                "auroc_loser": auroc_map[loser],
                "delta_auroc": delta,
                "ci_lower_winner": ci_lower_winner,
                "ci_upper_winner": ci_upper_winner,
                "ci_lower_loser": ci_lower_loser,
                "ci_upper_loser": ci_upper_loser,
                "ci_non_overlapping": ci_non_overlapping,
            })
    return results


def check_must_work_gate(
    pairwise_results: List[Dict[str, Any]],
    cfg: ExperimentConfig,
) -> Dict[str, Any]:
    """Check MUST_WORK gate: any pair with delta_auroc >= 0.05 AND non-overlapping CIs."""
    qualifying_pairs = []
    for pair in pairwise_results:
        meets_gap = pair["delta_auroc"] >= cfg.min_auroc_gap
        meets_ci = pair["ci_lower_winner"] > pair["ci_upper_loser"] + cfg.min_ci_separation
        if meets_gap and meets_ci:
            qualifying_pairs.append(pair)

    gate_passed = len(qualifying_pairs) > 0

    # Check directional hypothesis: semantic_entropy > token_entropy_mean
    se_auroc = None
    te_auroc = None
    for pair in pairwise_results:
        if "semantic_entropy" in (pair["method_a"], pair["method_b"]) and \
           "token_entropy_mean" in (pair["method_a"], pair["method_b"]):
            se_auroc = next((pair["auroc_winner"] if pair["winner"] == "semantic_entropy"
                            else pair["auroc_loser"] for _ in [1]), None)
            te_auroc = next((pair["auroc_winner"] if pair["winner"] == "token_entropy_mean"
                            else pair["auroc_loser"] for _ in [1]), None)

    direction_satisfied = None
    if se_auroc is not None and te_auroc is not None:
        direction_satisfied = se_auroc >= te_auroc

    return {
        "gate_type": "MUST_WORK",
        "gate_passed": gate_passed,
        "qualifying_pairs": qualifying_pairs,
        "qualifying_pair_count": len(qualifying_pairs),
        "alpha_corrected": cfg.alpha / cfg.bonferroni_k,
        "min_auroc_gap": cfg.min_auroc_gap,
        "min_ci_separation": cfg.min_ci_separation,
        "direction_satisfied": direction_satisfied,
        "message": "MUST_WORK gate: SATISFIED" if gate_passed else "MUST_WORK gate: NOT SATISFIED",
    }


def save_results(
    auroc_map: Dict[str, float],
    ci_map: Dict[str, Tuple[float, float]],
    pairwise_results: List[Dict[str, Any]],
    gate_result: Dict[str, Any],
    results_dir: str,
) -> None:
    Path(results_dir).mkdir(parents=True, exist_ok=True)

    full_results = {
        "auroc": auroc_map,
        "confidence_intervals_95": {k: {"lower": v[0], "upper": v[1]} for k, v in ci_map.items()},
        "pairwise_comparisons": pairwise_results,
        "gate": gate_result,
    }
    with open(Path(results_dir) / "h_e1_results.json", "w") as f:
        json.dump(full_results, f, indent=2)

    with open(Path(results_dir) / "h_e1_gate_check.json", "w") as f:
        json.dump(gate_result, f, indent=2)
