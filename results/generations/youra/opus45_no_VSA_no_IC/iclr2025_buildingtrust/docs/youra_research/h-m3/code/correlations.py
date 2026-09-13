"""Correlation analysis for H-M3 (FactScore distinctness)."""

import numpy as np
import pandas as pd
from scipy.stats import spearmanr


def compute_factscore_correlations(
    df: pd.DataFrame,
    factscore_col: str = "factscore",
    truthfulqa_col: str = "truthfulqa_mc2",
    halueval_col: str = "halueval_agg",
) -> dict[str, tuple[float, float]]:
    """Compute Spearman correlations for FactScore vs other benchmarks."""
    results = {}

    # Primary: FactScore vs TruthfulQA
    r, p = spearmanr(df[factscore_col], df[truthfulqa_col])
    results["fs_tqa"] = (float(r), float(p))

    # Primary: FactScore vs HaluEval
    r, p = spearmanr(df[factscore_col], df[halueval_col])
    results["fs_he"] = (float(r), float(p))

    # Reference: TruthfulQA vs HaluEval (from H-M2)
    r, p = spearmanr(df[truthfulqa_col], df[halueval_col])
    results["tqa_he"] = (float(r), float(p))

    return results


def bootstrap_ci(
    x: np.ndarray,
    y: np.ndarray,
    n_bootstrap: int = 1000,
    ci: float = 0.95,
    seed: int = 42,
) -> tuple[float, float]:
    """Percentile bootstrap CI for Spearman correlation."""
    if len(x) < 3:
        return (0.0, 1.0)

    rng = np.random.default_rng(seed)
    n = len(x)
    rs = []

    for _ in range(n_bootstrap):
        idx = rng.integers(0, n, n)
        r, _ = spearmanr(x[idx], y[idx])
        if not np.isnan(r):
            rs.append(r)

    if len(rs) < 10:
        return (0.0, 1.0)

    alpha = 1 - ci
    return (float(np.percentile(rs, 100 * alpha / 2)),
            float(np.percentile(rs, 100 * (1 - alpha / 2))))


def check_gate(
    results: dict[str, tuple[float, float]],
    threshold: float = 0.7,
) -> dict:
    """Evaluate PASS/PARTIAL/FAIL for H-M3 gate.

    Primary: r(FS,TQA) < 0.7 AND r(FS,HE) < 0.7
    """
    r_fs_tqa = results["fs_tqa"][0]
    r_fs_he = results["fs_he"][0]

    cond_tqa = abs(r_fs_tqa) < threshold
    cond_he = abs(r_fs_he) < threshold

    if cond_tqa and cond_he:
        status = "PASS"
    elif cond_tqa or cond_he:
        status = "PARTIAL"
    else:
        status = "FAIL"

    return {
        "status": status,
        "r_fs_tqa": r_fs_tqa,
        "r_fs_he": r_fs_he,
        "threshold": threshold,
        "cond_tqa_pass": cond_tqa,
        "cond_he_pass": cond_he,
    }
