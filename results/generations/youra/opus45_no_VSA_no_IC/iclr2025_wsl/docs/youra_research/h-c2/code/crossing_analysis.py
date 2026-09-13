"""Crossing point analysis for H-C2: Find N* where NFN matches Statistics R²."""
import numpy as np
from typing import List, Dict, Any, Optional
from scipy.stats import ttest_rel


def aggregate_by_n(results: List[Dict]) -> Dict[int, Dict[str, Any]]:
    """Aggregate results by N value, compute mean/std and 95% CI."""
    n_values = sorted(set(r["n"] for r in results))
    agg = {}

    for n in n_values:
        rows = [r for r in results if r["n"] == n]
        nfn_scores = [r["r2_nfn"] for r in rows]
        stats_scores = [r["r2_stats"] for r in rows]

        n_seeds = len(rows)
        ci_mult = 1.96 / np.sqrt(n_seeds) if n_seeds > 1 else 0

        agg[n] = {
            "n": n,
            "n_seeds": n_seeds,
            "mean_r2_nfn": float(np.mean(nfn_scores)),
            "std_r2_nfn": float(np.std(nfn_scores)),
            "ci_r2_nfn": float(np.std(nfn_scores) * ci_mult),
            "mean_r2_stats": float(np.mean(stats_scores)),
            "std_r2_stats": float(np.std(stats_scores)),
            "ci_r2_stats": float(np.std(stats_scores) * ci_mult),
            "delta": float(np.mean(nfn_scores) - np.mean(stats_scores)),
        }

    return agg


def find_crossing_point(
    agg: Dict[int, Dict], threshold: float = 0.03
) -> Optional[int]:
    """Find smallest N where |NFN R² - Stats R²| < threshold.

    Scans N ascending. Returns first N with |delta| < threshold.
    Returns None if no crossing found (gate failure).
    """
    for n in sorted(agg.keys()):
        if abs(agg[n]["delta"]) < threshold:
            return n
    return None


def crossing_point_report(
    agg: Dict[int, Dict], n_star: Optional[int], max_n: int = 2500
) -> Dict[str, Any]:
    """Generate crossing point report for gate evaluation.

    Gate: SHOULD_WORK - N* exists at N* < max_n
    """
    if n_star is not None and n_star < max_n:
        gate_result = "PASS"
        message = f"Crossing point N*={n_star} found (< {max_n})"
    elif n_star is not None:
        gate_result = "FAIL"
        message = f"Crossing point N*={n_star} exceeds limit ({max_n})"
    else:
        gate_result = "FAIL"
        message = f"No crossing point found in tested range"

    n_values = sorted(agg.keys())
    trends = {
        "nfn_trend": [agg[n]["mean_r2_nfn"] for n in n_values],
        "stats_trend": [agg[n]["mean_r2_stats"] for n in n_values],
        "delta_trend": [agg[n]["delta"] for n in n_values],
    }

    nfn_increasing = all(
        trends["nfn_trend"][i] <= trends["nfn_trend"][i+1]
        for i in range(len(trends["nfn_trend"]) - 1)
    )
    stats_increasing = all(
        trends["stats_trend"][i] <= trends["stats_trend"][i+1]
        for i in range(len(trends["stats_trend"]) - 1)
    )

    return {
        "n_star": n_star,
        "gate_result": gate_result,
        "message": message,
        "n_values_tested": n_values,
        "aggregated": {str(k): v for k, v in agg.items()},
        "trends": trends,
        "nfn_monotonic_increasing": nfn_increasing,
        "stats_monotonic_increasing": stats_increasing,
    }


def statistical_test(
    results: List[Dict], n: int
) -> Dict[str, float]:
    """Paired t-test for NFN vs Stats at given N."""
    rows = [r for r in results if r["n"] == n]
    nfn_scores = [r["r2_nfn"] for r in rows]
    stats_scores = [r["r2_stats"] for r in rows]

    if len(rows) < 2:
        return {"t_stat": float('nan'), "p_value": float('nan')}

    t_stat, p_value = ttest_rel(nfn_scores, stats_scores)
    return {"t_stat": float(t_stat), "p_value": float(p_value)}
