"""Gate verification and transfer correlation analysis for H-M4."""
from scipy import stats
import numpy as np

from config import BASELINES, TREATMENTS, GATE_THRESHOLD_PP, TASKS


def verify_gate(results: dict[str, dict[str, float]], baselines: list[str] = None,
                treatments: list[str] = None, threshold_pp: float = None) -> dict:
    """Per-metric: baseline_max, best_treatment, improvement_pp, pass. gate_pass = any(pass)."""
    baselines = baselines or BASELINES
    treatments = treatments or TREATMENTS
    threshold_pp = threshold_pp if threshold_pp is not None else GATE_THRESHOLD_PP

    verification = {}
    for metric in ["truthfulqa_mc1", "truthfulqa_mc2", "bbq"]:
        baseline_max = max(results[b][metric] for b in baselines)
        best_t_name = max(treatments, key=lambda t: results[t][metric])
        best_t = results[best_t_name][metric]
        improvement_pp = (best_t - baseline_max) * 100

        verification[metric] = {
            "baseline_max": baseline_max,
            "best_treatment": best_t_name,
            "best_treatment_value": best_t,
            "improvement_pp": improvement_pp,
            "pass": improvement_pp >= threshold_pp,
        }

        print(f"  {metric}: baseline_max={baseline_max:.3f}, "
              f"best_T={best_t_name}={best_t:.3f}, Δ={improvement_pp:.1f}pp "
              f"{'✓' if improvement_pp >= threshold_pp else '✗'}")

    gate_pass = any(v["pass"] for v in verification.values())
    print(f"\nGate: {'PASS' if gate_pass else 'FAIL'} (need ≥{threshold_pp}pp improvement)")

    return {"per_metric": verification, "gate_pass": gate_pass}


def statistical_significance(t_scores: list[float], b_scores: list[float],
                             alpha: float = 0.05) -> dict:
    """Two-tailed t-test. Returns t_statistic/p_value/significant."""
    t_stat, p_value = stats.ttest_ind(t_scores, b_scores)
    return {
        "t_statistic": float(t_stat),
        "p_value": float(p_value),
        "significant": p_value < alpha,
    }


def correlate_transfer(ifeval_gains: dict[str, float],
                       safety_gains: dict[str, float]) -> dict:
    """Pearson r between IFEval Δ and safety Δ per treatment."""
    keys = sorted(set(ifeval_gains) & set(safety_gains))
    if len(keys) < 3:
        return {"correlation": float("nan"), "p_value": 1.0,
                "interpretation": "insufficient_data", "significant": False}

    x = [ifeval_gains[k] for k in keys]
    y = [safety_gains[k] for k in keys]

    r, p = stats.pearsonr(x, y)
    interpretation = "positive" if r > 0 else "negative" if r < 0 else "none"

    print(f"  Correlation (IFEval Δ vs Safety Δ): r={r:.3f}, p={p:.3f} "
          f"({interpretation}, {'significant' if p < 0.05 else 'not significant'})")

    return {
        "correlation": float(r),
        "p_value": float(p),
        "interpretation": interpretation,
        "significant": p < 0.05,
        "ifeval_gains": ifeval_gains,
        "safety_gains": safety_gains,
    }


def compute_safety_gains(results: dict[str, dict[str, float]],
                         metric: str = "truthfulqa_mc1",
                         baseline: str = "b2") -> dict[str, float]:
    """Compute safety gains for treatments vs baseline."""
    baseline_val = results[baseline][metric]
    return {t: results[t][metric] - baseline_val for t in TREATMENTS}
