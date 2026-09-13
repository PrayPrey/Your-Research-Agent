"""H-E1 Evaluation: BIC Comparison and Gate Checks"""
import numpy as np
import pandas as pd
from config import EVAL


def compute_bic(residuals: np.ndarray, n_params: int, n_samples: int) -> float:
    """BIC = n*log(RSS/n) + n_params*log(n)."""
    residuals = np.asarray(residuals)
    rss = np.sum(residuals ** 2)

    if rss <= 0:
        rss = 1e-10  # avoid log(0)

    bic = n_samples * np.log(rss / n_samples) + n_params * np.log(n_samples)
    return bic


def compare_models(bic_mono: float, bic_seg: float) -> dict:
    """Compare BIC of monotonic vs segmented model."""
    delta = bic_mono - bic_seg
    return {
        "improvement": bic_seg < bic_mono,
        "delta": delta,
        "bic_mono": bic_mono,
        "bic_seg": bic_seg
    }


def check_target_window(
    change_points: list,
    dates: pd.DatetimeIndex,
    window: tuple = None
) -> list:
    """Filter change_points whose date.year falls in target window."""
    window = window or EVAL.target_window

    if not change_points or dates is None or len(dates) == 0:
        return []

    target_cps = []
    for cp in change_points:
        if cp < len(dates):
            year = dates[cp].year
            if window[0] <= year <= window[1]:
                target_cps.append(cp)

    return target_cps


def run_gate_checks(
    gini_series: np.ndarray,
    dates: pd.DatetimeIndex,
    change_points: list,
    bic_mono: float,
    bic_seg: float
) -> dict:
    """Aggregate PASS/FAIL for all success criteria.

    Gates:
    G-1: Change point in target window (2019-2022)
    G-2: Statistical significance (BIC improvement)
    G-3: BIC improvement (segmented < monotonic)
    """
    # G-1: Change point in window
    target_cps = check_target_window(change_points, dates)
    cp_in_window = len(target_cps) > 0

    # G-2/G-3: BIC improvement
    bic_improved = bic_seg < bic_mono
    bic_delta = bic_mono - bic_seg

    # Overall gate
    overall = "PASS" if (cp_in_window and bic_improved) else "FAIL"

    reasons = []
    if not cp_in_window:
        reasons.append(f"No change point in target window {EVAL.target_window}")
    if not bic_improved:
        reasons.append(f"BIC not improved: segmented={bic_seg:.2f} >= mono={bic_mono:.2f}")

    return {
        "overall": overall,
        "cp_in_window": cp_in_window,
        "target_cps": target_cps,
        "bic_improved": bic_improved,
        "bic_delta": bic_delta,
        "bic_mono": bic_mono,
        "bic_seg": bic_seg,
        "reasons": reasons,
        "num_change_points": len(change_points),
        "all_change_points": change_points
    }


if __name__ == "__main__":
    # Test with mock data
    dates = pd.date_range("2018-01-01", periods=72, freq="MS")
    change_points = [24, 48]  # ~2020 and ~2022

    residuals_mono = np.random.normal(0, 0.05, 72)
    residuals_seg = np.random.normal(0, 0.03, 72)  # better fit

    bic_mono = compute_bic(residuals_mono, n_params=2, n_samples=72)
    bic_seg = compute_bic(residuals_seg, n_params=6, n_samples=72)  # 3 segments = 6 params

    print(f"BIC mono: {bic_mono:.2f}")
    print(f"BIC seg: {bic_seg:.2f}")

    gates = run_gate_checks(np.zeros(72), dates, change_points, bic_mono, bic_seg)
    print(f"\nGate results: {gates['overall']}")
    for k, v in gates.items():
        print(f"  {k}: {v}")
