"""Mann-Kendall trend test and gate evaluation."""
import numpy as np
from scipy.stats import kendalltau


def run_mann_kendall(series: dict[str, float]) -> tuple[float, float]:
    """Mann-Kendall trend test via Kendall's tau against time index."""
    bins = sorted(series.keys())
    values = [series[b] for b in bins]
    time_idx = np.arange(len(values))
    tau, p_value = kendalltau(time_idx, values)
    return float(tau), float(p_value)


def evaluate_success(
    results: dict[str, tuple[float, float]],
    p_threshold: float = 0.05,
    effect_threshold: float = 0.2,
    min_passing: int = 2,
) -> dict:
    """Evaluate H-E1 gate: >=min_passing proxies with p<p_threshold."""
    out = {}
    n_pass = 0
    effect_pass = False
    for proxy, (tau, p) in results.items():
        passed = p < p_threshold
        if passed:
            n_pass += 1
        if abs(tau) > effect_threshold:
            effect_pass = True
        out[proxy] = {"tau": tau, "p_value": p, "abs_tau": abs(tau), "pass": passed}
    out["overall_pass"] = n_pass >= min_passing
    out["n_passing"] = n_pass
    out["effect_pass"] = effect_pass
    return out
