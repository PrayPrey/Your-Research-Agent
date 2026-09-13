"""analyzer.py — Segment split, variance stats, F-test, Brown-Forsythe for H-M1."""
from __future__ import annotations
from typing import Tuple, TypedDict

import numpy as np
from scipy import stats


class AnalysisResults(TypedDict):
    n_pre: int
    n_post: int
    global_variance: float
    global_mean: float
    pre_variance: float
    pre_mean: float
    post_variance: float
    post_mean: float
    F_stat: float
    p_one_tailed: float
    variance_ratio_pre_global: float
    pre_mean_positive: bool
    bf_stat: float
    bf_p: float
    gate_passed: bool


def compute_global_variance(residual_cov: np.ndarray) -> Tuple[float, float]:
    """Return (global_variance, global_mean) for full N=111 series."""
    return float(np.var(residual_cov, ddof=1)), float(np.mean(residual_cov))


def split_segments(
    residual_cov: np.ndarray,
    paper_count_star_idx: int,
) -> Tuple[np.ndarray, np.ndarray]:
    """Split residual_cov at idx; return (pre, post). Raises if len(pre) < 3."""
    pre = residual_cov[:paper_count_star_idx]
    post = residual_cov[paper_count_star_idx:]
    if len(pre) < 3:
        raise ValueError(f"pre_segment length={len(pre)} < 3 (min_pre_segment_n=3)")
    return pre, post


def run_f_test(
    pre: np.ndarray,
    global_var: float,
    n_total: int,
) -> Tuple[float, float, float]:
    """One-sample F-test: H1 = pre_var > global_var (one-tailed, right tail).

    Returns:
        F_stat, p_one_tailed, variance_ratio_pre_global

    Raises:
        ValueError: if len(pre) < 2 or global_var <= 0
    """
    if len(pre) < 2:
        raise ValueError(f"pre-segment too small (n={len(pre)}) — need at least 2 for ddof=1 variance")
    if global_var <= 0:
        raise ValueError(f"global_var={global_var} <= 0 — degenerate input")

    pre_var = float(np.var(pre, ddof=1))
    F_stat = pre_var / global_var
    df1 = len(pre) - 1
    df2 = n_total - 1
    p_one_tailed = float(1.0 - stats.f.cdf(F_stat, df1, df2))
    variance_ratio_pre_global = F_stat

    return F_stat, p_one_tailed, variance_ratio_pre_global


def run_brown_forsythe(pre: np.ndarray, post: np.ndarray) -> Tuple[float, float]:
    """scipy.stats.levene with center='median' = Brown-Forsythe test."""
    bf_stat, bf_p = stats.levene(pre, post, center="median")
    return float(bf_stat), float(bf_p)


def analyze(residual_cov: np.ndarray, paper_count_star_idx: int) -> AnalysisResults:
    """Full analysis pipeline. Returns AnalysisResults dict."""
    N = len(residual_cov)

    global_var, global_mean = compute_global_variance(residual_cov)
    print(f"Global variance (N={N}): {global_var:.6f}")

    pre, post = split_segments(residual_cov, paper_count_star_idx)
    n_pre, n_post = len(pre), len(post)
    assert n_pre + n_post == N, f"Segment split mismatch: {n_pre}+{n_post} != {N}"

    pre_var = float(np.var(pre, ddof=1))
    pre_mean = float(np.mean(pre))
    post_var = float(np.var(post, ddof=1))
    post_mean = float(np.mean(post))
    print(f"Pre-segment N={n_pre}, variance={pre_var:.6f}, global_var={global_var:.6f}")

    F_stat, p_one_tailed, variance_ratio_pre_global = run_f_test(pre, global_var, N)
    print(f"F-test: F={F_stat:.4f}, p_one_tailed={p_one_tailed:.4f}, ratio={variance_ratio_pre_global:.4f}")

    pre_mean_positive = pre_mean > 0
    print(f"Pre-segment mean: {pre_mean:.6f} ({'POSITIVE' if pre_mean_positive else 'NEGATIVE'})")

    bf_stat, bf_p = run_brown_forsythe(pre, post)
    print(f"Brown-Forsythe pre vs post: stat={bf_stat:.4f}, p={bf_p:.4f}")

    gate_passed = (p_one_tailed < 0.10) and (variance_ratio_pre_global > 1.0)
    print(f"GATE: {'PASS' if gate_passed else 'FAIL'} (p={p_one_tailed:.4f}, ratio={variance_ratio_pre_global:.4f})")

    return AnalysisResults(
        n_pre=n_pre,
        n_post=n_post,
        global_variance=global_var,
        global_mean=global_mean,
        pre_variance=pre_var,
        pre_mean=pre_mean,
        post_variance=post_var,
        post_mean=post_mean,
        F_stat=F_stat,
        p_one_tailed=p_one_tailed,
        variance_ratio_pre_global=variance_ratio_pre_global,
        pre_mean_positive=pre_mean_positive,
        bf_stat=bf_stat,
        bf_p=bf_p,
        gate_passed=gate_passed,
    )
