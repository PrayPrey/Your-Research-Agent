"""
Metrics module for H-E1 AUROC experiment.

AUROC computation, bootstrap CI, and gate evaluation.
"""

import numpy as np
from sklearn.metrics import roc_auc_score

from config import BOOTSTRAP_N, SEED


def compute_auroc_with_ci(
    margins: np.ndarray,
    correctness: np.ndarray,
    n_bootstrap: int = BOOTSTRAP_N,
    seed: int = SEED,
) -> dict[str, float]:
    """
    Compute AUROC with bootstrap 95% CI.

    Args:
        margins: Array of margin values
        correctness: Array of correctness labels (0/1)
        n_bootstrap: Number of bootstrap iterations
        seed: Random seed for reproducibility

    Returns:
        Dict with 'auroc', 'ci_lower', 'ci_upper'
    """
    rng = np.random.default_rng(seed)

    # Handle edge cases
    if len(np.unique(correctness)) < 2:
        # All same class - AUROC undefined
        return {"auroc": 0.5, "ci_lower": 0.5, "ci_upper": 0.5}

    # Compute point estimate
    auroc = roc_auc_score(correctness, margins)

    # Bootstrap CI
    n = len(margins)
    bootstrap_aurocs = []

    for _ in range(n_bootstrap):
        indices = rng.choice(n, n, replace=True)
        boot_correct = correctness[indices]
        boot_margins = margins[indices]

        # Skip if all same class in bootstrap sample
        if len(np.unique(boot_correct)) < 2:
            continue

        boot_auroc = roc_auc_score(boot_correct, boot_margins)
        bootstrap_aurocs.append(boot_auroc)

    if len(bootstrap_aurocs) == 0:
        return {"auroc": auroc, "ci_lower": auroc, "ci_upper": auroc}

    ci_lower = float(np.percentile(bootstrap_aurocs, 2.5))
    ci_upper = float(np.percentile(bootstrap_aurocs, 97.5))

    return {"auroc": float(auroc), "ci_lower": ci_lower, "ci_upper": ci_upper}


def compute_conditional_margins(
    margins: np.ndarray,
    correctness: np.ndarray,
) -> dict[str, float]:
    """
    Compute mean margins conditioned on correctness.

    Args:
        margins: Array of margin values
        correctness: Array of correctness labels (0/1)

    Returns:
        Dict with 'mean_correct' and 'mean_incorrect'
    """
    correct_mask = correctness == 1
    incorrect_mask = correctness == 0

    mean_correct = float(np.mean(margins[correct_mask])) if correct_mask.any() else 0.0
    mean_incorrect = float(np.mean(margins[incorrect_mask])) if incorrect_mask.any() else 0.0

    return {"mean_correct": mean_correct, "mean_incorrect": mean_incorrect}


def compute_i2_statistic(
    deltas: list[float],
    ci_lowers: list[float],
    ci_uppers: list[float],
) -> float:
    """
    Compute I^2 heterogeneity statistic for meta-analysis.

    Args:
        deltas: List of effect sizes (AUROC differences)
        ci_lowers: Lower CI bounds
        ci_uppers: Upper CI bounds

    Returns:
        I^2 statistic (0-100%)
    """
    k = len(deltas)
    if k < 2:
        return 0.0

    # Estimate variance from CI width (assuming normal approximation)
    variances = []
    for lower, upper in zip(ci_lowers, ci_uppers):
        # CI width / 3.92 ≈ SE (for 95% CI)
        se = (upper - lower) / 3.92
        variances.append(se ** 2)

    # Inverse variance weights
    weights = [1.0 / v if v > 0 else 0 for v in variances]
    total_weight = sum(weights)

    if total_weight == 0:
        return 0.0

    # Weighted mean
    weighted_mean = sum(w * d for w, d in zip(weights, deltas)) / total_weight

    # Q statistic (weighted sum of squared deviations)
    Q = sum(w * (d - weighted_mean) ** 2 for w, d in zip(weights, deltas))

    # I^2 = (Q - (k-1)) / Q
    if Q > k - 1:
        i2 = 100 * (Q - (k - 1)) / Q
    else:
        i2 = 0.0

    return float(i2)


def evaluate_gate_criteria(results: dict) -> dict[str, bool]:
    """
    Evaluate MUST_WORK gate criteria.

    Criteria:
    1. AUROC_base > AUROC_instruct for each family
    2. 95% CI of delta excludes zero (ci_lower > 0)

    Args:
        results: Dict with per-family results containing 'base' and 'instruct' AUROC metrics

    Returns:
        Dict with per-family pass status and 'all_pass' boolean
    """
    gate_results = {}

    for family in ["qwen", "llama", "mistral"]:
        if family not in results:
            gate_results[family] = False
            continue

        family_data = results[family]
        base_auroc = family_data["base"]["auroc"]
        inst_auroc = family_data["instruct"]["auroc"]

        # Compute delta and CI
        delta = base_auroc - inst_auroc

        # Bootstrap delta CI (approximate from individual CIs)
        # Delta CI ≈ delta ± sqrt(SE_base^2 + SE_inst^2) * 1.96
        base_se = (family_data["base"]["ci_upper"] - family_data["base"]["ci_lower"]) / 3.92
        inst_se = (family_data["instruct"]["ci_upper"] - family_data["instruct"]["ci_lower"]) / 3.92
        delta_se = np.sqrt(base_se**2 + inst_se**2)
        delta_ci_lower = delta - 1.96 * delta_se

        # Check criteria
        direction_pass = base_auroc > inst_auroc
        ci_pass = delta_ci_lower > 0

        gate_results[family] = direction_pass and ci_pass

    gate_results["all_pass"] = all(gate_results.get(f, False) for f in ["qwen", "llama", "mistral"])

    return gate_results
