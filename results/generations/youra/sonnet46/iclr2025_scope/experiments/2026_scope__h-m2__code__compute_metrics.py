from itertools import combinations
from typing import Dict, List, Tuple

import numpy as np
from scipy.stats import kendalltau, variation

from config import ExperimentConfig

ADJACENT_PAIRS = [(0.001, 0.01), (0.01, 0.05), (0.05, 0.1)]


def compute_cv_per_epsilon(
    sparsity_dict: Dict[float, np.ndarray],
    epsilons: List[float],
) -> Dict[float, float]:
    """Compute coefficient of variation (std/mean) per epsilon."""
    result = {}
    for eps in epsilons:
        sv = sparsity_dict[eps]
        mean_val = float(sv.mean())
        if mean_val == 0:
            result[eps] = float("nan")
        else:
            result[eps] = float(variation(sv))
    return result


def count_cv_pass(
    cv_per_epsilon: Dict[float, float],
    threshold: float = 0.3,
) -> Tuple[int, Dict[float, bool]]:
    """Count how many epsilon values pass CV > threshold."""
    passed = {eps: (cv > threshold if not np.isnan(cv) else False)
              for eps, cv in cv_per_epsilon.items()}
    return sum(passed.values()), passed


def compute_cross_epsilon_tau(
    sparsity_dict: Dict[float, np.ndarray],
    epsilons: List[float],
) -> Dict[str, Dict[str, float]]:
    """Compute all 6 pairwise Kendall tau_b values across epsilon conditions."""
    results = {}
    for e1, e2 in combinations(epsilons, 2):
        key = f"{e1}_vs_{e2}"
        tau, p_value = kendalltau(sparsity_dict[e1], sparsity_dict[e2], variant='b')
        results[key] = {"tau": float(tau), "p_value": float(p_value)}
    return results


def compute_cross_dist_tau(
    alpaca_sparsity: Dict[float, np.ndarray],
    wikitext_sparsity: Dict[float, np.ndarray],
    epsilons: List[float],
) -> Dict[float, Dict[str, float]]:
    """Compute Alpaca vs WikiText Kendall tau per epsilon (secondary metric)."""
    results = {}
    for eps in epsilons:
        tau, p_value = kendalltau(alpaca_sparsity[eps], wikitext_sparsity[eps], variant='b')
        results[eps] = {"tau": float(tau), "p_value": float(p_value)}
    return results


def evaluate_gate(
    cv_per_epsilon: Dict[float, float],
    tau_matrix: Dict[str, Dict[str, float]],
    cfg: ExperimentConfig,
) -> Tuple[bool, Dict]:
    """Evaluate MUST_WORK gate for H-M2.

    Gate criteria:
      1. CV > cv_threshold for >= cv_pass_min_count epsilon values
      2. max adjacent-pair tau >= cross_epsilon_tau_threshold
    """
    cv_pass_count, cv_pass_dict = count_cv_pass(cv_per_epsilon, cfg.cv_threshold)
    cv_gate_passed = cv_pass_count >= cfg.cv_pass_min_count

    adjacent_tau = {}
    for (e1, e2) in ADJACENT_PAIRS:
        key = f"{e1}_vs_{e2}"
        if key in tau_matrix:
            adjacent_tau[key] = tau_matrix[key]["tau"]

    max_adjacent_tau = max(adjacent_tau.values()) if adjacent_tau else 0.0
    tau_gate_passed = max_adjacent_tau >= cfg.cross_epsilon_tau_threshold

    gate_pass = cv_gate_passed and tau_gate_passed

    failed_conditions = []
    if not cv_gate_passed:
        failed_conditions.append(
            f"CV pass count={cv_pass_count} < {cfg.cv_pass_min_count}"
        )
    if not tau_gate_passed:
        failed_conditions.append(
            f"max adjacent tau={max_adjacent_tau:.4f} < {cfg.cross_epsilon_tau_threshold}"
        )

    return gate_pass, {
        "gate_result": "PASS" if gate_pass else "FAIL",
        "cv_pass_count": cv_pass_count,
        "cv_pass_dict": {str(k): v for k, v in cv_pass_dict.items()},
        "max_adjacent_tau": max_adjacent_tau,
        "adjacent_pair_results": adjacent_tau,
        "failed_conditions": failed_conditions,
        "all_tau_pairs": tau_matrix,
    }


def verify_mechanism_activated(
    sparsity_dict: Dict[float, np.ndarray],
    tau_matrix: Dict,
    epsilons: List[float],
) -> Tuple[bool, Dict]:
    """Sanity check that data is complete and values are valid."""
    data_complete = all(len(sparsity_dict.get(eps, [])) == 32 for eps in epsilons)
    tau_complete = len(tau_matrix) == 6 if tau_matrix else True
    values_valid = all(
        0.0 < float(sparsity_dict[eps].mean()) < 1.0
        for eps in epsilons
        if eps in sparsity_dict
    )
    indicators = {
        "data_complete": data_complete,
        "tau_complete": tau_complete,
        "values_valid": values_valid,
    }
    return all(indicators.values()), indicators
