import numpy as np


def bootstrap_ci(distances, n_boot=1000, seed=42, ci=0.95):
    rng = np.random.default_rng(seed)
    arr = np.array(distances)
    n = len(arr)
    indices = rng.integers(0, n, size=(n_boot, n))
    boot_means = arr[indices].mean(axis=1)
    alpha = (1.0 - ci) / 2.0
    return float(np.quantile(boot_means, alpha)), float(np.quantile(boot_means, 1.0 - alpha))


def aggregate(distances, threshold=0.05, n_boot=1000, seed=42):
    arr = np.array(distances)
    ci_lower, ci_upper = bootstrap_ci(distances, n_boot=n_boot, seed=seed)
    return {
        "mean": float(arr.mean()),
        "std": float(arr.std()),
        "p5": float(np.percentile(arr, 5)),
        "p95": float(np.percentile(arr, 95)),
        "frac_above": float((arr > threshold).mean()),
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
    }


def evaluate_gate(stats):
    s = stats["scaling"]
    passed = (
        s["mean"] > 0.05
        and s["frac_above"] >= 0.90
        and s["ci_lower"] > 0
    )
    cond = (
        f"mean={s['mean']:.4f}>0.05: {s['mean']>0.05}, "
        f"frac_above={s['frac_above']:.4f}>=0.90: {s['frac_above']>=0.90}, "
        f"ci_lower={s['ci_lower']:.4f}>0: {s['ci_lower']>0}"
    )
    return {
        "pass": passed,
        "mean_cosine_scaling": s["mean"],
        "frac_above_scaling": s["frac_above"],
        "ci_lower_scaling": s["ci_lower"],
        "gate_condition": cond,
    }
