"""Statistical testing for H-M2."""
from typing import List, Dict, Tuple, Any
from scipy.stats import ttest_rel
import numpy as np

import config


def paired_ttest(r2_nfn_scores: List[float], r2_mlp_scores: List[float]) -> Tuple[float, float]:
    """Paired t-test. Returns (t_stat, p_value)."""
    t_stat, p_value = ttest_rel(r2_nfn_scores, r2_mlp_scores)
    return float(t_stat), float(p_value)


def summarize_n(results: List[Dict], n: int) -> Dict[str, Any]:
    """Summary stats for a single N value across seeds."""
    rows = [r for r in results if r["n"] == n]
    nfn_scores = [r["r2_nfn"] for r in rows]
    mlp_scores = [r["r2_mlp"] for r in rows]
    deltas = [a - b for a, b in zip(nfn_scores, mlp_scores)]

    t_stat, p_value = paired_ttest(nfn_scores, mlp_scores)

    mean_delta = float(np.mean(deltas))
    passed = mean_delta >= config.R2_DELTA_TARGET and p_value < config.ALPHA

    return {
        "n": n,
        "mean_r2_nfn": float(np.mean(nfn_scores)),
        "std_r2_nfn": float(np.std(nfn_scores)),
        "mean_r2_mlp": float(np.mean(mlp_scores)),
        "std_r2_mlp": float(np.std(mlp_scores)),
        "mean_delta": mean_delta,
        "std_delta": float(np.std(deltas)),
        "t_stat": t_stat,
        "p_value": p_value,
        "pass": passed,
    }


def summarize_all(results: List[Dict]) -> Dict[int, Dict[str, Any]]:
    """Summary for all N values."""
    n_values = sorted(set(r["n"] for r in results))
    return {n: summarize_n(results, n) for n in n_values}
