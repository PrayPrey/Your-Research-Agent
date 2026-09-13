from __future__ import annotations
import numpy as np
import ruptures as rpt
from scipy.stats import linregress
from config import CFG


def ols_detrend(
    paper_counts: np.ndarray,
    cov_values: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, dict]:
    """Sort by paper_count, OLS fit CoV ~ paper_count, return residuals."""
    paper_counts = np.asarray(paper_counts, dtype=float)
    cov_values = np.asarray(cov_values, dtype=float)

    if len(paper_counts) < 2:
        raise ValueError(f"Insufficient data for OLS: N={len(paper_counts)}")
    if cov_values.std() == 0:
        raise ValueError("Zero variance in CoV — degenerate input")

    sort_idx = np.argsort(paper_counts, kind="stable")
    sorted_pc = paper_counts[sort_idx]
    sorted_cov = cov_values[sort_idx]

    slope, intercept, rho, p_value, _ = linregress(sorted_pc, sorted_cov)
    r2 = float(rho) ** 2
    fitted = slope * sorted_pc + intercept
    residual_cov = sorted_cov - fitted

    ols_metrics = {
        "slope": float(slope),
        "intercept": float(intercept),
        "rho": float(rho),
        "r2": float(r2),
        "p_value": float(p_value),
    }
    return sorted_pc, residual_cov, ols_metrics


def run_pelt_changepoint(
    paper_counts: np.ndarray,
    cov_values: np.ndarray,
    pen_range: tuple = None,
    n_pen: int = None,
    min_size: int = None,
) -> dict:
    """OLS detrend + PELT change-point detection with BIC penalty."""
    if pen_range is None:
        pen_range = CFG.pen_range
    if n_pen is None:
        n_pen = CFG.n_pen
    if min_size is None:
        min_size = CFG.pelt_min_size

    sorted_pc, residual_cov, ols_metrics = ols_detrend(paper_counts, cov_values)
    T = len(residual_cov)

    # BIC penalty (L2 cost, Killick et al. 2012)
    sigma = residual_cov.std(ddof=1)
    bic_pen = sigma ** 2 * np.log(T)

    # Penalty sensitivity sweep
    pen_values = np.logspace(
        np.log10(pen_range[0]),
        np.log10(pen_range[1]),
        n_pen,
    )
    algo = rpt.Pelt(model=CFG.pelt_model, min_size=min_size, jump=CFG.pelt_jump)
    algo.fit(residual_cov)
    bkps_list = [algo.predict(pen=float(p)) for p in pen_values]

    # Primary detection at BIC penalty
    bkps = algo.predict(pen=float(bic_pen))
    n_bkps = len(bkps) - 1  # last element is T (end sentinel)

    if n_bkps >= 1:
        bkp_idx = bkps[0] - 1  # ruptures is 1-based; convert to 0-based
        paper_count_star = float(sorted_pc[bkp_idx])
    else:
        bkp_idx = None
        paper_count_star = None

    print(
        f"PELT: {n_bkps} breakpoint(s) at idx={bkp_idx}, "
        f"paper_count*={paper_count_star}, BIC_pen={bic_pen:.4f}"
    )

    return {
        "paper_count_star": paper_count_star,
        "breakpoint_idx": bkp_idx,
        "pen_used": float(bic_pen),
        "n_bkps": n_bkps,
        "residual_cov_sorted": residual_cov,
        "sorted_paper_counts": sorted_pc,
        "bkps_list": bkps_list,
        "pen_values": pen_values,
        "ols_metrics": ols_metrics,
    }
