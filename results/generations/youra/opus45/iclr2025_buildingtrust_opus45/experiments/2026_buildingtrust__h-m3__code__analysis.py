"""Per-family analysis pipeline for H-M3 Brier decomposition.

Implements paired bootstrap difference test to compare refinement
between base and instruct models.
"""
import numpy as np
from typing import Optional

from config import SEED, BOOTSTRAP_N, N_BINS, P_VALUE_THRESHOLD
from brier_decomp import (
    margin_to_confidence,
    murphy_brier_decomposition,
    bootstrap_decomposition,
    compute_ci,
)


def paired_bootstrap_difference(
    base_margins: np.ndarray,
    base_correctness: np.ndarray,
    inst_margins: np.ndarray,
    inst_correctness: np.ndarray,
    component: str,
    n_iterations: int = BOOTSTRAP_N,
    n_bins: int = N_BINS,
    seed: int = SEED,
) -> dict[str, float]:
    """Paired bootstrap test for component difference (base - instruct).

    Uses paired resampling to compute the difference in a Brier component
    between base and instruct models, preserving the sample pairing.

    Args:
        base_margins: (N,) margins for base model
        base_correctness: (N,) correctness for base model
        inst_margins: (N,) margins for instruct model
        inst_correctness: (N,) correctness for instruct model
        component: Component to test (e.g., 'refinement', 'reliability')
        n_iterations: Number of bootstrap iterations
        n_bins: Number of bins for decomposition
        seed: Random seed

    Returns:
        Dictionary with:
            - delta_mean: Mean difference (base - instruct)
            - delta_ci_lower: Lower 95% CI bound
            - delta_ci_upper: Upper 95% CI bound
            - p_value: Proportion of deltas <= 0
            - effect_size: Cohen's d (delta_mean / std(deltas))
    """
    N = len(base_margins)
    rng = np.random.RandomState(seed)

    # Convert margins to confidences
    base_conf = margin_to_confidence(base_margins)
    inst_conf = margin_to_confidence(inst_margins)

    deltas = np.zeros(n_iterations)

    for i in range(n_iterations):
        # Paired resampling: same indices for both models
        idx = rng.choice(N, size=N, replace=True)

        try:
            # Decompose base model
            base_decomp = murphy_brier_decomposition(
                base_conf[idx], base_correctness[idx], n_bins
            )
            # Decompose instruct model
            inst_decomp = murphy_brier_decomposition(
                inst_conf[idx], inst_correctness[idx], n_bins
            )

            # Delta = base - instruct
            # For refinement: positive delta means base has HIGHER refinement (better discrimination)
            deltas[i] = base_decomp[component] - inst_decomp[component]

        except ValueError:
            deltas[i] = np.nan

    # Remove NaN values
    valid_deltas = deltas[~np.isnan(deltas)]

    if len(valid_deltas) == 0:
        return {
            "delta_mean": np.nan,
            "delta_ci_lower": np.nan,
            "delta_ci_upper": np.nan,
            "p_value": np.nan,
            "effect_size": np.nan,
        }

    delta_mean = np.mean(valid_deltas)
    delta_ci_lower = np.percentile(valid_deltas, 2.5)
    delta_ci_upper = np.percentile(valid_deltas, 97.5)

    # p-value: proportion where delta <= 0 (null hypothesis: base <= instruct)
    p_value = np.mean(valid_deltas <= 0)

    # Effect size: Cohen's d
    delta_std = np.std(valid_deltas)
    effect_size = delta_mean / delta_std if delta_std > 0 else 0.0

    return {
        "delta_mean": delta_mean,
        "delta_ci_lower": delta_ci_lower,
        "delta_ci_upper": delta_ci_upper,
        "p_value": p_value,
        "effect_size": effect_size,
    }


def analyze_family(
    family: str,
    data: dict[str, np.ndarray],
) -> dict:
    """Full per-family analysis pipeline.

    Computes:
    1. Point estimates for Brier decomposition (base and instruct)
    2. Bootstrap CIs for each component
    3. Paired difference test for refinement
    4. Gate evaluation

    Args:
        family: Model family name
        data: Dictionary with keys: base_margins, base_correctness,
              inst_margins, inst_correctness

    Returns:
        Structured results dictionary
    """
    # Convert margins to confidences
    base_conf = margin_to_confidence(data["base_margins"])
    inst_conf = margin_to_confidence(data["inst_margins"])

    # Point estimates
    base_decomp = murphy_brier_decomposition(
        base_conf, data["base_correctness"]
    )
    inst_decomp = murphy_brier_decomposition(
        inst_conf, data["inst_correctness"]
    )

    # Bootstrap CIs for each model
    base_bootstrap = bootstrap_decomposition(base_conf, data["base_correctness"])
    inst_bootstrap = bootstrap_decomposition(inst_conf, data["inst_correctness"])

    base_cis = {}
    inst_cis = {}
    for component in ["brier_score", "reliability", "resolution", "refinement", "uncertainty"]:
        base_cis[component] = compute_ci(base_bootstrap[component])
        inst_cis[component] = compute_ci(inst_bootstrap[component])

    # Paired difference test for refinement
    refinement_diff = paired_bootstrap_difference(
        data["base_margins"],
        data["base_correctness"],
        data["inst_margins"],
        data["inst_correctness"],
        component="refinement",
    )

    # Also test reliability for completeness
    reliability_diff = paired_bootstrap_difference(
        data["base_margins"],
        data["base_correctness"],
        data["inst_margins"],
        data["inst_correctness"],
        component="reliability",
    )

    # Gate evaluation for this family
    # H-M3 hypothesis: Refinement degrades in instruct models (refinement_instruct < refinement_base)
    # This means delta (base - instruct) should be POSITIVE
    refinement_direction_correct = refinement_diff["delta_mean"] > 0
    ci_excludes_zero = refinement_diff["delta_ci_lower"] > 0
    p_significant = refinement_diff["p_value"] < P_VALUE_THRESHOLD

    gate_pass = refinement_direction_correct and p_significant

    return {
        "family": family,
        "n_samples": len(data["base_margins"]),
        "base": {
            "decomposition": base_decomp,
            "confidence_intervals": base_cis,
        },
        "instruct": {
            "decomposition": inst_decomp,
            "confidence_intervals": inst_cis,
        },
        "refinement_difference": refinement_diff,
        "reliability_difference": reliability_diff,
        "gate_pass": gate_pass,
        "gate_details": {
            "direction_correct": refinement_direction_correct,
            "ci_excludes_zero": ci_excludes_zero,
            "p_significant": p_significant,
        },
    }


def evaluate_gate(family_results: dict[str, dict]) -> str:
    """Evaluate overall gate result across all families.

    Args:
        family_results: Dictionary mapping family -> analysis results

    Returns:
        'PASS' if all families pass, else 'FAIL'
    """
    all_pass = all(r["gate_pass"] for r in family_results.values())
    return "PASS" if all_pass else "FAIL"
