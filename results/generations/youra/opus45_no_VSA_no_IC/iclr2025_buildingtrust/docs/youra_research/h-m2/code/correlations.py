"""Correlation analysis for H-M2."""

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from itertools import combinations


def compute_halueval_correlations(
    df: pd.DataFrame,
    truthfulqa_col: str = "truthfulqa_mc2",
    halueval_cols: list[str] = None,
) -> dict[str, tuple[float, float]]:
    """Compute Spearman correlations: cross-benchmark and intra-HaluEval."""
    if halueval_cols is None:
        halueval_cols = ["halueval_qa", "halueval_dialogue", "halueval_summarization"]

    results = {}

    # Aggregate HaluEval score
    halueval_agg = df[halueval_cols].mean(axis=1)

    # Primary: HaluEval aggregate vs TruthfulQA
    r, p = spearmanr(halueval_agg, df[truthfulqa_col])
    results["halueval_vs_truthfulqa"] = (float(r), float(p))

    # Per-subtask cross-correlations
    for col in halueval_cols:
        subtask = col.replace("halueval_", "")
        r, p = spearmanr(df[col], df[truthfulqa_col])
        results[f"{subtask}_vs_truthfulqa"] = (float(r), float(p))

    # Intra-HaluEval correlations (3 pairs)
    for col1, col2 in combinations(halueval_cols, 2):
        name1 = col1.replace("halueval_", "")
        name2 = col2.replace("halueval_", "")
        r, p = spearmanr(df[col1], df[col2])
        results[f"{name1}_vs_{name2}"] = (float(r), float(p))

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
        return (-1.0, 1.0)

    rng = np.random.default_rng(seed)
    n = len(x)
    rs = []

    for _ in range(n_bootstrap):
        idx = rng.integers(0, n, n)
        r, _ = spearmanr(x[idx], y[idx])
        if not np.isnan(r):
            rs.append(r)

    if len(rs) < 10:
        return (-1.0, 1.0)

    alpha = 1 - ci
    lo = np.percentile(rs, 100 * alpha / 2)
    hi = np.percentile(rs, 100 * (1 - alpha / 2))
    return (float(lo), float(hi))


def check_gate(
    results: dict[str, tuple[float, float]],
    threshold: float = 0.7,
) -> dict:
    """Evaluate PASS/PARTIAL/FAIL based on gate conditions.

    Primary: r(HaluEval_agg, TruthfulQA) < 0.7
    Secondary: mean(r_intra) > r_cross (HaluEval subtasks correlate more with each other)
    """
    r_cross = results["halueval_vs_truthfulqa"][0]

    # Intra-HaluEval pairs (those without "truthfulqa" in the key)
    intra_keys = [k for k in results if "_vs_" in k and "truthfulqa" not in k]
    intra_rs = [results[k][0] for k in intra_keys]
    r_intra_mean = float(np.mean(intra_rs)) if intra_rs else 0.0

    primary_pass = r_cross < threshold
    secondary_pass = r_intra_mean > r_cross

    if primary_pass and secondary_pass:
        status = "PASS"
    elif primary_pass:
        status = "PARTIAL"
    else:
        status = "FAIL"

    return {
        "status": status,
        "r_cross": r_cross,
        "r_intra_mean": r_intra_mean,
        "threshold": threshold,
        "primary_pass": primary_pass,
        "secondary_pass": secondary_pass,
    }
