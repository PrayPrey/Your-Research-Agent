import json
import logging
from dataclasses import dataclass
from typing import Dict, List

import numpy as np
from scipy import stats

logger = logging.getLogger(__name__)


@dataclass
class GateResult:
    """Gate evaluation output for H-E1."""
    condition_a_mean: float
    condition_b_mean: float
    condition_p_mean: float
    t_stat: float
    p_value: float
    gate_pass: bool        # LS_A > LS_P AND p < 0.05
    secondary_pass: bool   # LS_A > LS_B (informational)


def one_sided_ttest_ls_a_gt_p(
    ls_scores_a: List[float],
    ls_scores_p: List[float],
    alpha: float = 0.05,
) -> GateResult:
    """One-sided t-test H0: LS_A - LS_P <= 0.
    Uses scipy.stats.ttest_1samp(np.array(ls_a) - np.array(ls_p), 0, alternative='greater').
    """
    arr_a = np.array(ls_scores_a, dtype=np.float64)
    arr_p = np.array(ls_scores_p, dtype=np.float64)

    # Align lengths
    min_len = min(len(arr_a), len(arr_p))
    arr_a = arr_a[:min_len]
    arr_p = arr_p[:min_len]

    diff = arr_a - arr_p
    if len(diff) < 2:
        # Degenerate case: single sample
        t_stat = float(diff[0]) if len(diff) == 1 else 0.0
        p_value = 0.0 if (len(diff) == 1 and diff[0] > 0) else 1.0
    else:
        t_result = stats.ttest_1samp(diff, 0, alternative="greater")
        t_stat  = float(t_result.statistic)  # type: ignore[union-attr]
        p_value = float(t_result.pvalue)     # type: ignore[union-attr]

    mean_a = float(arr_a.mean()) if len(arr_a) > 0 else 0.0
    mean_p = float(arr_p.mean()) if len(arr_p) > 0 else 0.0
    gate_pass = (mean_a > mean_p) and (p_value < alpha)

    return GateResult(
        condition_a_mean=mean_a,
        condition_b_mean=0.0,   # filled in evaluate_gate
        condition_p_mean=mean_p,
        t_stat=t_stat,
        p_value=p_value,
        gate_pass=gate_pass,
        secondary_pass=False,   # filled in evaluate_gate
    )


def evaluate_gate(
    ls_by_condition: Dict[str, List[float]],
    dataset_name: str,
    alpha: float = 0.05,
) -> GateResult:
    """Compute GateResult for a given dataset's LS scores."""
    ls_a = ls_by_condition.get("A", [])
    ls_b = ls_by_condition.get("B", [])
    ls_p = ls_by_condition.get("P", [])

    result = one_sided_ttest_ls_a_gt_p(ls_a, ls_p, alpha=alpha)

    mean_b = float(np.mean(ls_b)) if ls_b else 0.0
    mean_a = result.condition_a_mean
    result.condition_b_mean = mean_b
    result.secondary_pass   = mean_a > mean_b

    logger.info(f"Gate evaluation [{dataset_name}]: pass={result.gate_pass}, p={result.p_value:.4f}")
    return result


def log_gate_result(result: GateResult, dataset_name: str) -> None:
    """Print gate results in the required format."""
    print(
        f"[H-E1] Locality Score — "
        f"Condition A: {result.condition_a_mean:.4f} | "
        f"Condition B: {result.condition_b_mean:.4f} | "
        f"Condition P: {result.condition_p_mean:.4f}"
    )
    print(
        f"[H-E1] Gate Check: LS_A > LS_P = {result.gate_pass} "
        f"(p={result.p_value:.4f})"
    )
    logger.info(
        f"[H-E1][{dataset_name}] LS_A={result.condition_a_mean:.4f} "
        f"LS_B={result.condition_b_mean:.4f} "
        f"LS_P={result.condition_p_mean:.4f} "
        f"gate={'PASS' if result.gate_pass else 'FAIL'} p={result.p_value:.4f}"
    )


def write_results_json(results: dict, output_path: str) -> None:
    """Serialize all LS scores, gate results, and metadata to JSON."""
    import os
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)

    def _serializable(obj):
        if hasattr(obj, "gate_pass") and hasattr(obj, "t_stat"):
            return {
                "condition_a_mean": obj.condition_a_mean,
                "condition_b_mean": obj.condition_b_mean,
                "condition_p_mean": obj.condition_p_mean,
                "t_stat": obj.t_stat,
                "p_value": obj.p_value,
                "gate_pass": obj.gate_pass,
                "secondary_pass": obj.secondary_pass,
            }
        if isinstance(obj, np.ndarray):  # type: ignore[misc]
            return obj.tolist()
        if isinstance(obj, (np.float32, np.float64)):
            return float(obj)
        return obj

    def _convert(obj):
        if isinstance(obj, dict):
            return {k: _convert(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_convert(v) for v in obj]
        return _serializable(obj)

    with open(output_path, "w") as f:
        json.dump(_convert(results), f, indent=2)
    logger.info(f"Results written to {output_path}")
