"""H-M2 Analyzer: Brown-Forsythe pre-vs-post + variance ratio + piecewise F-test."""
from __future__ import annotations

from typing import Tuple, TypedDict

import numpy as np
from scipy import stats


class VarianceCompressionResults(TypedDict):
    n_pre: int
    n_post: int
    var_pre: float
    var_post: float
    mean_pre: float
    mean_post: float
    variance_ratio: float
    bf_stat: float
    bf_p_two_tailed: float
    bf_p_one_tailed: float
    direction_confirmed: bool
    piecewise_f_stat: float
    piecewise_f_p: float
    gate_passed: bool


def split_segments(
    residual_cov: np.ndarray,
    paper_count_star_idx: int,
) -> Tuple[np.ndarray, np.ndarray]:
    """Return (pre, post) segments split at paper_count_star_idx."""
    pre = residual_cov[:paper_count_star_idx]
    post = residual_cov[paper_count_star_idx:]
    if len(pre) < 3:
        raise ValueError(f"Pre-segment too small: n_pre={len(pre)} < 3")
    if len(post) < 3:
        raise ValueError(f"Post-segment too small: n_post={len(post)} < 3")
    return pre, post


def run_brown_forsythe_pre_post(
    pre: np.ndarray,
    post: np.ndarray,
) -> Tuple[float, float, float, float]:
    """BF test (center='median') pre vs post.

    Returns: (bf_stat, bf_p_two_tailed, bf_p_one_tailed, variance_ratio)
    center='median' is mandatory — this is Brown-Forsythe, not Levene.
    """
    bf_stat, bf_p_two_tailed = stats.levene(pre, post, center="median")
    var_pre = float(np.var(pre, ddof=1))
    var_post = float(np.var(post, ddof=1))
    variance_ratio = var_post / var_pre if var_pre > 0 else float("inf")
    direction_confirmed = variance_ratio < 1.0
    bf_p_one_tailed = bf_p_two_tailed / 2.0 if direction_confirmed else 1.0
    print(
        f"Brown-Forsythe: stat={bf_stat:.4f}, p_two={bf_p_two_tailed:.4f},"
        f" p_one={bf_p_one_tailed:.4f}"
    )
    return float(bf_stat), float(bf_p_two_tailed), float(bf_p_one_tailed), float(variance_ratio)


def run_piecewise_f_test(
    paper_counts: np.ndarray,
    residual_cov: np.ndarray,
    paper_count_star_idx: int,
) -> Tuple[float, float]:
    """Nested OLS F-test: baseline vs piecewise model.

    Returns: (f_stat, f_p)
    """
    import statsmodels.api as sm
    from scipy.stats import f as f_dist

    N = len(paper_counts)
    if not (0 < paper_count_star_idx < N):
        raise ValueError(f"paper_count_star_idx={paper_count_star_idx} not in (0, {N})")

    regime = (paper_counts >= paper_counts[paper_count_star_idx]).astype(int)

    X_base = sm.add_constant(paper_counts.astype(float))
    model_base = sm.OLS(residual_cov, X_base).fit()
    rss_base = float(model_base.ssr)
    p_base = X_base.shape[1]  # 2

    interaction = paper_counts.astype(float) * regime
    X_piece = np.column_stack([
        np.ones(N),
        paper_counts.astype(float),
        regime,
        interaction,
    ])
    model_piece = sm.OLS(residual_cov, X_piece).fit()
    rss_piece = float(model_piece.ssr)
    p_piece = X_piece.shape[1]  # 4

    q = p_piece - p_base  # 2
    df_den = N - p_piece
    if df_den <= 0 or q <= 0:
        raise ValueError(f"Degenerate F-test: df_num={q}, df_den={df_den}")

    numerator = (rss_base - rss_piece) / q
    denominator = rss_piece / df_den
    f_stat = max(0.0, numerator / denominator) if denominator > 0 else 0.0
    f_p = float(1.0 - f_dist.cdf(f_stat, q, df_den))

    print(f"Piecewise regression F-test: F={f_stat:.4f}, p={f_p:.4f} (df={q},{df_den})")
    return float(f_stat), f_p


def analyze(
    paper_counts: np.ndarray,
    residual_cov: np.ndarray,
    paper_count_star_idx: int,
) -> VarianceCompressionResults:
    """Full analysis: split → BF → variance ratio → piecewise F → gate."""
    pre, post = split_segments(residual_cov, paper_count_star_idx)

    n_pre = len(pre)
    n_post = len(post)
    var_pre = float(np.var(pre, ddof=1))
    var_post = float(np.var(post, ddof=1))
    mean_pre = float(np.mean(pre))
    mean_post = float(np.mean(post))

    print(
        f"Segments: n_pre={n_pre}, n_post={n_post},"
        f" var_pre={var_pre:.6f}, var_post={var_post:.6f}"
    )

    bf_stat, bf_p_two_tailed, bf_p_one_tailed, variance_ratio = run_brown_forsythe_pre_post(
        pre, post
    )
    direction_confirmed = variance_ratio < 1.0
    print(f"Variance ratio (post/pre): {variance_ratio:.4f}, direction_confirmed={direction_confirmed}")

    piecewise_f_stat, piecewise_f_p = run_piecewise_f_test(
        paper_counts, residual_cov, paper_count_star_idx
    )

    gate_passed = bool(bf_p_two_tailed < 0.05 and variance_ratio < 1.0)
    fail_reasons = []
    if bf_p_two_tailed >= 0.05:
        fail_reasons.append(f"BF p={bf_p_two_tailed:.4f} >= 0.05")
    if variance_ratio >= 1.0:
        fail_reasons.append(f"variance_ratio={variance_ratio:.4f} >= 1.0")
    verdict = "PASS" if gate_passed else f"FAIL ({'; '.join(fail_reasons)})"
    print(
        f"GATE: {verdict} — BF p={bf_p_two_tailed:.4f} (threshold 0.05),"
        f" ratio={variance_ratio:.4f} (threshold 1.0)"
    )

    return VarianceCompressionResults(
        n_pre=n_pre,
        n_post=n_post,
        var_pre=var_pre,
        var_post=var_post,
        mean_pre=mean_pre,
        mean_post=mean_post,
        variance_ratio=variance_ratio,
        bf_stat=bf_stat,
        bf_p_two_tailed=bf_p_two_tailed,
        bf_p_one_tailed=bf_p_one_tailed,
        direction_confirmed=direction_confirmed,
        piecewise_f_stat=piecewise_f_stat,
        piecewise_f_p=piecewise_f_p,
        gate_passed=gate_passed,
    )
