"""evaluate.py — ECE computation, bootstrap CI, null baseline, sensitivity analysis, gate."""
from __future__ import annotations

import warnings
from typing import Any

import numpy as np

from .config import (
    DELTA_ECE_THRESHOLD,
    M_PRIMARY,
    M_SENSITIVITY,
    N_BOOT,
    P1_MIN_PASSING,
    SEED,
)


def compute_ece(
    confidences: np.ndarray,
    labels: np.ndarray,
    M: int = 15,
) -> float:
    """Compute Expected Calibration Error (Guo 2017).

    Bins: np.linspace(0, 1, M+1)
    - First bin: confidence <= bin_edges[1] (includes 0.0)
    - Subsequent bins: (bin_edges[k-1], bin_edges[k]]

    Parameters
    ----------
    confidences : array of predicted confidence scores in [0, 1]
    labels : array of binary ground-truth labels
    M : number of bins

    Returns
    -------
    ECE as float, or float('nan') if input is empty
    """
    confidences = np.asarray(confidences, dtype=float)
    labels = np.asarray(labels, dtype=float)

    if len(confidences) == 0:
        warnings.warn("compute_ece: empty input, returning nan.")
        return float("nan")

    bin_edges = np.linspace(0.0, 1.0, M + 1)
    n = len(confidences)
    ece = 0.0

    for k in range(M):
        lower = bin_edges[k]
        upper = bin_edges[k + 1]

        if k == 0:
            # First bin: includes 0.0
            mask = confidences <= upper
        else:
            mask = (confidences > lower) & (confidences <= upper)

        n_bin = mask.sum()
        if n_bin == 0:
            continue

        avg_conf = confidences[mask].mean()
        avg_acc = labels[mask].mean()
        ece += (n_bin / n) * abs(avg_conf - avg_acc)

    return float(ece)


def compute_tier_ece(
    c_hard: np.ndarray,
    y_hard: np.ndarray,
    c_easy: np.ndarray,
    y_easy: np.ndarray,
    M: int = 15,
) -> dict[str, float]:
    """Compute ECE for hard and easy tiers and delta ECE.

    Returns
    -------
    dict with keys: ece_hard, ece_easy, delta_ece
    where delta_ece = ece_hard - ece_easy
    """
    ece_hard = compute_ece(c_hard, y_hard, M=M)
    ece_easy = compute_ece(c_easy, y_easy, M=M)
    delta_ece = ece_hard - ece_easy

    return {
        "ece_hard": ece_hard,
        "ece_easy": ece_easy,
        "delta_ece": delta_ece,
    }


def compute_delta_ece_bootstrap(
    c_hard: np.ndarray,
    y_hard: np.ndarray,
    c_easy: np.ndarray,
    y_easy: np.ndarray,
    n_boot: int = 1000,
    M: int = 15,
    seed: int = 42,
    return_samples: bool = False,
) -> tuple[float, float, float, float] | tuple[float, float, float, float, np.ndarray]:
    """Bootstrap confidence interval for delta ECE = ECE_hard - ECE_easy.

    Parameters
    ----------
    c_hard, y_hard : hard tier data
    c_easy, y_easy : easy tier data
    n_boot : number of bootstrap samples
    M : number of ECE bins
    seed : random seed
    return_samples : if True, also return array of bootstrap delta ECE values

    Returns
    -------
    (delta_ece_obs, ci_lower, ci_upper, p_value) or with boot_deltas appended
    - delta_ece_obs : observed delta ECE
    - ci_lower, ci_upper : 2.5th and 97.5th percentiles
    - p_value : fraction of bootstrap samples <= 0 (one-tailed)
    """
    c_hard = np.asarray(c_hard, dtype=float)
    y_hard = np.asarray(y_hard, dtype=float)
    c_easy = np.asarray(c_easy, dtype=float)
    y_easy = np.asarray(y_easy, dtype=float)

    rng = np.random.default_rng(seed)

    n_hard = len(c_hard)
    n_easy = len(c_easy)

    # Observed delta ECE
    delta_ece_obs = compute_ece(c_hard, y_hard, M=M) - compute_ece(c_easy, y_easy, M=M)

    boot_deltas = np.empty(n_boot, dtype=float)
    for i in range(n_boot):
        idx_hard = rng.integers(0, n_hard, size=n_hard)
        idx_easy = rng.integers(0, n_easy, size=n_easy)

        boot_c_hard = c_hard[idx_hard]
        boot_y_hard = y_hard[idx_hard]
        boot_c_easy = c_easy[idx_easy]
        boot_y_easy = y_easy[idx_easy]

        ece_h = compute_ece(boot_c_hard, boot_y_hard, M=M)
        ece_e = compute_ece(boot_c_easy, boot_y_easy, M=M)
        boot_deltas[i] = ece_h - ece_e

    if np.all(boot_deltas == boot_deltas[0]):
        warnings.warn("compute_delta_ece_bootstrap: all bootstrap samples are identical.")

    ci_lower, ci_upper = np.percentile(boot_deltas, [2.5, 97.5])
    p_value = float(np.mean(boot_deltas <= 0))

    if return_samples:
        return float(delta_ece_obs), float(ci_lower), float(ci_upper), float(p_value), boot_deltas

    return float(delta_ece_obs), float(ci_lower), float(ci_upper), float(p_value)


def compute_null_baseline(
    c_hard: np.ndarray,
    y_hard: np.ndarray,
    c_easy: np.ndarray,
    y_easy: np.ndarray,
    M: int = 15,
) -> dict[str, float]:
    """Compute null baseline ECE using constant (mean) confidence per tier.

    A null model that always predicts the mean accuracy of each tier.
    Compares observed ECE vs null ECE to show excess calibration error.

    Returns
    -------
    dict with keys: ece_hard, ece_easy, delta_ece, null_ece_hard, null_ece_easy,
                    null_delta_ece, excess_ece_hard, excess_ece_easy
    """
    c_hard = np.asarray(c_hard, dtype=float)
    y_hard = np.asarray(y_hard, dtype=float)
    c_easy = np.asarray(c_easy, dtype=float)
    y_easy = np.asarray(y_easy, dtype=float)

    # Observed ECE
    ece_hard = compute_ece(c_hard, y_hard, M=M)
    ece_easy = compute_ece(c_easy, y_easy, M=M)
    delta_ece = ece_hard - ece_easy

    # Null: constant confidence = mean label (base rate)
    null_conf_hard = float(y_hard.mean()) if len(y_hard) > 0 else 0.5
    null_conf_easy = float(y_easy.mean()) if len(y_easy) > 0 else 0.5

    null_c_hard = np.full_like(c_hard, null_conf_hard)
    null_c_easy = np.full_like(c_easy, null_conf_easy)

    null_ece_hard = compute_ece(null_c_hard, y_hard, M=M)
    null_ece_easy = compute_ece(null_c_easy, y_easy, M=M)
    null_delta_ece = null_ece_hard - null_ece_easy

    excess_ece_hard = ece_hard - null_ece_hard
    excess_ece_easy = ece_easy - null_ece_easy

    return {
        "ece_hard": ece_hard,
        "ece_easy": ece_easy,
        "delta_ece": delta_ece,
        "null_ece_hard": null_ece_hard,
        "null_ece_easy": null_ece_easy,
        "null_delta_ece": null_delta_ece,
        "excess_ece_hard": excess_ece_hard,
        "excess_ece_easy": excess_ece_easy,
    }


def compute_m_sensitivity(
    c_hard: np.ndarray,
    y_hard: np.ndarray,
    c_easy: np.ndarray,
    y_easy: np.ndarray,
    m_values: list[int] | None = None,
) -> dict[int, float]:
    """Compute delta ECE for different bin counts M.

    Parameters
    ----------
    m_values : list of M values to evaluate (default: [10, 15, 20])

    Returns
    -------
    {M: delta_ece}
    """
    if m_values is None:
        m_values = M_SENSITIVITY

    result: dict[int, float] = {}
    for M in m_values:
        tier_result = compute_tier_ece(c_hard, y_hard, c_easy, y_easy, M=M)
        result[M] = tier_result["delta_ece"]

    return result


def evaluate_gate(
    model_results: dict[str, dict[str, Any]],
    threshold: float = 0.03,
    min_passing: int = 2,
) -> tuple[bool, int]:
    """Evaluate primary gate: count models passing delta_ece >= threshold AND ci_lower > 0.

    Parameters
    ----------
    model_results : {model_short: {delta_ece, ci_lower, ci_upper, p_value, ...}}
    threshold : minimum delta ECE required (default 0.03)
    min_passing : minimum number of models that must pass (default 2)

    Returns
    -------
    (gate_pass, n_passing)
    """
    n_passing = 0
    for model_short, res in model_results.items():
        delta_ece = res.get("delta_ece", 0.0)
        ci_lower = res.get("ci_lower", 0.0)
        if delta_ece >= threshold and ci_lower > 0:
            n_passing += 1

    gate_pass = n_passing >= min_passing
    return gate_pass, n_passing


def verify_mechanism_activated(
    ece_hard: float,
    ece_easy: float,
    delta_ece: float,
    n_hard: int,
    n_easy: int,
    ci_lower: float,
    ci_upper: float,
) -> tuple[bool, dict[str, bool]]:
    """Verify that the calibration mechanism is activated.

    Checks five indicators to confirm the experiment is working as expected.

    Parameters
    ----------
    ece_hard : ECE for hard tier
    ece_easy : ECE for easy tier
    delta_ece : ece_hard - ece_easy
    n_hard : number of hard samples
    n_easy : number of easy samples
    ci_lower : lower bound of bootstrap CI
    ci_upper : upper bound of bootstrap CI

    Returns
    -------
    (all_pass, indicators_dict)
    """
    indicators: dict[str, bool] = {
        "data_loaded": (n_hard > 0) and (n_easy > 0),
        "ece_computed": not (np.isnan(ece_hard) or np.isnan(ece_easy)),
        "delta_nontrivial": abs(delta_ece) > 1e-6,
        "ci_computed": not (np.isnan(ci_lower) or np.isnan(ci_upper)),
        "effect_measured": ci_upper > ci_lower,
    }

    all_pass = all(indicators.values())
    return all_pass, indicators
