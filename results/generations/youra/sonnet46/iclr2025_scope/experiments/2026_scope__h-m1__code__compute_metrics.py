import itertools
from typing import Dict, Any
import numpy as np
from scipy.stats import kendalltau
from config import ExperimentConfig


def compute_cv(layer_sparsity: np.ndarray) -> float:
    """Coefficient of variation: std / mean. Guard against mean == 0."""
    mean = layer_sparsity.mean()
    if mean == 0.0:
        return 0.0
    return float(layer_sparsity.std() / mean)


def compute_kendall_tau(sparsity_a: np.ndarray, sparsity_b: np.ndarray):
    """Returns (tau_statistic, p_value) from scipy.stats.kendalltau."""
    tau, pval = kendalltau(sparsity_a, sparsity_b)
    return float(tau), float(pval)


def compute_all_metrics(condition_results: dict, cfg: ExperimentConfig) -> dict:
    """Compute CV and Kendall tau for all epsilon conditions. Returns flat metrics dict."""
    metrics = {}

    for eps in cfg.epsilons:
        eps_key = str(eps)

        alpaca_long   = condition_results[("alpaca",   eps, cfg.long_length)]
        alpaca_short  = condition_results[("alpaca",   eps, cfg.short_length)]
        wikitext_long = condition_results[("wikitext", eps, cfg.long_length)]

        cv = compute_cv(alpaca_long)
        metrics[f"cv_alpaca_long_eps{eps_key}"] = cv

        tau_cal, p_cal = compute_kendall_tau(alpaca_long, wikitext_long)
        metrics[f"tau_calibration_eps{eps_key}"]      = tau_cal
        metrics[f"tau_calibration_pval_eps{eps_key}"] = p_cal

        tau_len, p_len = compute_kendall_tau(alpaca_short, alpaca_long)
        metrics[f"tau_length_eps{eps_key}"]      = tau_len
        metrics[f"tau_length_pval_eps{eps_key}"] = p_len

    # Primary metrics
    primary = str(cfg.primary_epsilon)
    metrics["cv_primary"]           = metrics[f"cv_alpaca_long_eps{primary}"]
    metrics["tau_calibration"]      = metrics[f"tau_calibration_eps{primary}"]
    metrics["tau_calibration_pval"] = metrics[f"tau_calibration_pval_eps{primary}"]
    metrics["tau_length"]           = metrics[f"tau_length_eps{primary}"]
    metrics["tau_length_pval"]      = metrics[f"tau_length_pval_eps{primary}"]

    return metrics


def check_gate_conditions(metrics: dict, cfg: ExperimentConfig):
    """Check cv_primary > cv_threshold AND tau_calibration >= tau_threshold."""
    cv_val  = metrics["cv_primary"]
    tau_val = metrics["tau_calibration"]
    cv_pass  = cv_val  > cfg.cv_threshold
    tau_pass = tau_val >= cfg.tau_threshold
    passed = cv_pass and tau_pass
    return passed, {
        "cv_pass":  cv_pass,
        "tau_pass": tau_pass,
        "cv_value":  cv_val,
        "tau_value": tau_val,
    }


# ─── H-M1 extensions ──────────────────────────────────────────────────────────

def compute_pairwise_tau(
    sparsity_profiles: Dict[str, np.ndarray]
) -> Dict[str, Dict[str, float]]:
    """Compute all C(4,2)=6 pairwise Kendall's tau values.
    Returns: {pair_key: {tau: float, pval: float}} for all pairs."""
    dists = list(sparsity_profiles.keys())
    results = {}
    for d1, d2 in itertools.combinations(dists, 2):
        tau, pval = kendalltau(sparsity_profiles[d1], sparsity_profiles[d2])
        results[f"{d1}_vs_{d2}"] = {"tau": float(tau), "pval": float(pval)}
    return results


def compute_tau_min(tau_results: Dict[str, Dict[str, float]]) -> float:
    """Return the minimum tau across all pairwise comparisons."""
    return min(v["tau"] for v in tau_results.values())


def evaluate_gate(
    icc3k: float,
    tau_results: Dict[str, Dict[str, float]],
    cfg: ExperimentConfig,
) -> Dict[str, Any]:
    """Evaluate gate: PASS if icc3k > icc_threshold AND all 6 tau >= tau_threshold.
    Returns: {gate_result, icc3k, tau_min, tau_results, failed_conditions}"""
    tau_min = compute_tau_min(tau_results)
    icc_passed = icc3k > cfg.icc_threshold
    tau_passed = tau_min >= cfg.tau_threshold
    gate_result = "PASS" if (icc_passed and tau_passed) else "FAIL"
    failed = []
    if not icc_passed:
        failed.append(f"ICC3k={icc3k:.4f} <= {cfg.icc_threshold}")
    if not tau_passed:
        failed.append(f"tau_min={tau_min:.4f} < {cfg.tau_threshold}")
    return {
        "gate_result": gate_result,
        "icc3k": icc3k,
        "tau_min": tau_min,
        "icc_passed": icc_passed,
        "tau_passed": tau_passed,
        "failed_conditions": failed,
        "tau_results": tau_results,
    }


def compute_tau_sensitivity(
    sparsity_by_epsilon: Dict[float, Dict[str, np.ndarray]]
) -> Dict[float, Dict[str, Any]]:
    """Compute pairwise tau and tau_min for each epsilon value."""
    result = {}
    for eps, profiles in sparsity_by_epsilon.items():
        tau_results = compute_pairwise_tau(profiles)
        tau_min = compute_tau_min(tau_results)
        result[eps] = {"tau_min": tau_min, "tau_results": tau_results}
    return result
