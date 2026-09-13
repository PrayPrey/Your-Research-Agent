"""temperature_scaling.py — temperature scaling for confidence calibration."""
from __future__ import annotations

import warnings

import numpy as np
from scipy.optimize import minimize_scalar

from .config import N_BOOT, SEED, T_BOUNDS
from .evaluate import compute_ece, compute_delta_ece_bootstrap


def _nll_objective(T: float, confidences: np.ndarray, labels: np.ndarray) -> float:
    """Negative log-likelihood objective for temperature scaling.

    NLL = -mean(y * log(clip(c/T)) + (1-y) * log(1 - clip(c/T)))
    """
    eps = 1e-7
    scaled = np.clip(confidences / T, eps, 1.0 - eps)
    nll = -np.mean(labels * np.log(scaled) + (1.0 - labels) * np.log(1.0 - scaled))
    return float(nll)


def fit_temperature(
    c_holdout: np.ndarray,
    y_holdout: np.ndarray,
    bounds: tuple[float, float] = T_BOUNDS,
) -> float:
    """Fit temperature T to minimize NLL on holdout data.

    Parameters
    ----------
    c_holdout : confidence scores on holdout set
    y_holdout : binary labels on holdout set
    bounds : (T_min, T_max) search bounds

    Returns
    -------
    Optimal temperature T*, or float('nan') if optimization fails.
    """
    c_holdout = np.asarray(c_holdout, dtype=float)
    y_holdout = np.asarray(y_holdout, dtype=float)

    if len(c_holdout) == 0:
        warnings.warn("fit_temperature: empty holdout data, returning nan.")
        return float("nan")

    result = minimize_scalar(
        _nll_objective,
        bounds=bounds,
        method="bounded",
        args=(c_holdout, y_holdout),
    )

    if not result.success:
        warnings.warn(f"fit_temperature: optimization did not converge: {result.message}")
        return float("nan")

    return float(result.x)


def apply_temperature(confidences: np.ndarray, T: float) -> np.ndarray:
    """Apply temperature scaling: clip(c / T, 0, 1).

    Parameters
    ----------
    confidences : array of confidence scores
    T : temperature value

    Returns
    -------
    Temperature-scaled confidences clipped to [0, 1]
    """
    confidences = np.asarray(confidences, dtype=float)
    return np.clip(confidences / T, 0.0, 1.0)


def compute_post_T_metrics(
    eval_data: dict[str, np.ndarray],
    holdout_data: dict[str, np.ndarray],
    M: int = 15,
    n_boot: int = N_BOOT,
    seed: int = SEED,
) -> dict[str, float | bool]:
    """Fit temperature on holdout and evaluate post-scaling metrics on eval data.

    Parameters
    ----------
    eval_data : dict with c_hard, y_hard, c_easy, y_easy (evaluation split)
    holdout_data : dict with c_hard, y_hard, c_easy, y_easy (holdout split for T fitting)
    M : number of ECE bins
    n_boot : number of bootstrap iterations
    seed : random seed

    Returns
    -------
    dict with: T_star, post_T_ece_hard, post_T_ece_easy, post_T_delta_ece,
               post_T_ci_lower, post_T_ci_upper, post_T_p_value, gate_p3
    """
    # Combine holdout hard + easy to fit a single global temperature
    c_holdout_all = np.concatenate([holdout_data["c_hard"], holdout_data["c_easy"]])
    y_holdout_all = np.concatenate([holdout_data["y_hard"], holdout_data["y_easy"]])

    T_star = fit_temperature(c_holdout_all, y_holdout_all)

    if np.isnan(T_star):
        warnings.warn("compute_post_T_metrics: T_star is nan, using T=1.0 as fallback.")
        T_star = 1.0

    # Apply temperature scaling to eval data
    c_hard_scaled = apply_temperature(eval_data["c_hard"], T_star)
    c_easy_scaled = apply_temperature(eval_data["c_easy"], T_star)
    y_hard_eval = eval_data["y_hard"]
    y_easy_eval = eval_data["y_easy"]

    # Compute post-T ECE metrics
    post_T_ece_hard = compute_ece(c_hard_scaled, y_hard_eval, M=M)
    post_T_ece_easy = compute_ece(c_easy_scaled, y_easy_eval, M=M)
    post_T_delta_ece = post_T_ece_hard - post_T_ece_easy

    # Bootstrap CI on post-T delta ECE
    _, post_T_ci_lower, post_T_ci_upper, post_T_p_value = compute_delta_ece_bootstrap(
        c_hard_scaled,
        y_hard_eval,
        c_easy_scaled,
        y_easy_eval,
        n_boot=n_boot,
        M=M,
        seed=seed,
    )

    # Gate P3: post-T delta ECE still >= 0.03 with CI excluding zero
    gate_p3 = (post_T_delta_ece >= 0.03) and (post_T_ci_lower > 0)

    return {
        "T_star": float(T_star),
        "post_T_ece_hard": float(post_T_ece_hard),
        "post_T_ece_easy": float(post_T_ece_easy),
        "post_T_delta_ece": float(post_T_delta_ece),
        "post_T_ci_lower": float(post_T_ci_lower),
        "post_T_ci_upper": float(post_T_ci_upper),
        "post_T_p_value": float(post_T_p_value),
        "gate_p3": bool(gate_p3),
    }
