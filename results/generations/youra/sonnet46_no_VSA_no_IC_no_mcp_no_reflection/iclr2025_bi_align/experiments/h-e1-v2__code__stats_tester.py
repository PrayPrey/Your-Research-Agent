import numpy as np
import scipy.stats
import pymannkendall


def acf_lag1(series: np.ndarray) -> float:
    n = len(series)
    if n < 2:
        return 0.0
    mean = series.mean()
    num = np.sum((series[:-1] - mean) * (series[1:] - mean))
    denom = np.sum((series - mean) ** 2)
    return float(num / denom) if denom > 0 else 0.0


def mann_kendall(series: np.ndarray, acf_threshold: float = 0.1) -> dict:
    series = np.asarray(series, dtype=float)
    valid = series[~np.isnan(series)]
    if len(valid) < 4:
        return {"tau": 0.0, "p": 1.0, "significant": False, "method": "insufficient_data", "acf_lag1": 0.0, "n_months": len(valid)}

    time_idx = np.arange(len(valid))
    acf = acf_lag1(valid)

    if acf <= acf_threshold:
        tau, p = scipy.stats.kendalltau(time_idx, valid)
        method = "kendalltau"
    else:
        result = pymannkendall.hamed_rao_modification_test(valid)
        tau, p = result.Tau, result.p
        method = "hamed_rao"

    return {
        "tau": float(tau),
        "p": float(p),
        "significant": bool(p < 0.05 and abs(tau) > 0.0),
        "method": method,
        "acf_lag1": float(acf),
        "n_months": len(valid),
    }


def bootstrap_ci(series: np.ndarray, time_idx: np.ndarray, B: int = 1000, seed: int = 42) -> tuple:
    rng = np.random.default_rng(seed)
    n = len(series)
    tau_samples = np.empty(B)
    for i in range(B):
        idx = rng.integers(0, n, size=n)
        tau_samples[i], _ = scipy.stats.kendalltau(time_idx[idx], series[idx])
    return (float(np.percentile(tau_samples, 2.5)), float(np.percentile(tau_samples, 97.5)))


def evaluate_gate(results: dict, gate_min_significant: int = 2) -> dict:
    n_significant = sum(
        1 for v in results.get("proxies", {}).values()
        if isinstance(v, dict) and v.get("significant", False)
    )
    results["gate"] = {
        "n_significant": n_significant,
        "gate_passed": n_significant >= gate_min_significant,
    }
    return results
