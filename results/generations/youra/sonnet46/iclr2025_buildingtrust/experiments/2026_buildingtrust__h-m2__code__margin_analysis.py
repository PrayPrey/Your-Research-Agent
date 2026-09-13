"""
margin_analysis.py — H-M2 Pre-Softmax Logit Margin Inflation
Core margin computation: compute_logit_margins, bootstrap CI, gradient ordering test.
"""
import logging

import numpy as np
from scipy import stats

logger = logging.getLogger(__name__)


def compute_logit_margins(logprob_matrix: np.ndarray) -> np.ndarray:
    """Compute per-item top-1 minus top-2 log-prob margin.

    Args:
        logprob_matrix: (N, 4) float64 raw pre-softmax log-probs

    Returns:
        margins: (N,) float64 — all values >= 0 by construction
        (top-1 is always >= top-2 after sorting descending)
    """
    if logprob_matrix.ndim != 2 or logprob_matrix.shape[1] != 4:
        raise ValueError(
            f"Expected (N, 4) logprob_matrix, got shape {logprob_matrix.shape}"
        )
    if np.any(np.isnan(logprob_matrix)):
        raise ValueError("NaN values found in logprob_matrix")

    # Sort descending along choice axis
    sorted_logprobs = np.sort(logprob_matrix, axis=1)[:, ::-1]  # (N, 4) descending
    margins = sorted_logprobs[:, 0] - sorted_logprobs[:, 1]     # top-1 minus top-2
    assert np.all(margins >= 0), "margins should be non-negative after sorting"
    return margins.astype(np.float64)


def compute_delta_margin(
    base_logprobs: np.ndarray,
    aligned_logprobs: np.ndarray,
    n_bootstrap: int = 1000,
    seed: int = 42,
) -> tuple:
    """Bootstrap 95% CI for mean(aligned_margins) - mean(base_margins).

    Args:
        base_logprobs: (N, 4) float64
        aligned_logprobs: (N, 4) float64
        n_bootstrap: number of bootstrap samples
        seed: random seed

    Returns:
        (delta_mean, ci_lower_95, ci_upper_95) in nats

    Raises:
        ValueError if NaN present
        AssertionError if margins negative
    """
    base_margins = compute_logit_margins(base_logprobs)       # (N,)
    aligned_margins = compute_logit_margins(aligned_logprobs) # (N,)

    assert np.all(base_margins >= 0), "base margins must be non-negative"
    assert np.all(aligned_margins >= 0), "aligned margins must be non-negative"

    delta_per_item = aligned_margins - base_margins  # (N,) — may be negative

    if np.any(np.isnan(delta_per_item)):
        raise ValueError("NaN in delta_per_item after margin subtraction")

    delta_mean = float(np.mean(delta_per_item))
    N = len(delta_per_item)

    rng = np.random.RandomState(seed)
    boot_means = np.array([
        np.mean(rng.choice(delta_per_item, size=N, replace=True))
        for _ in range(n_bootstrap)
    ])

    ci_lower = float(np.percentile(boot_means, 2.5))
    ci_upper = float(np.percentile(boot_means, 97.5))

    return delta_mean, ci_lower, ci_upper


def compute_all_delta_margins(
    logprob_matrices: dict,
    sizes: list,
    alignments: list,
    n_bootstrap: int = 1000,
    seed: int = 42,
) -> dict:
    """Compute delta margins for all 9 alignment-size pairs.

    Args:
        logprob_matrices: {model_key: (N,4)} where model_key = "pythia-{size}-{alignment}"
        sizes: e.g. ["1.4b", "2.8b", "6.9b"]
        alignments: e.g. ["sft", "dpo", "ppo"]
        n_bootstrap: bootstrap samples
        seed: random seed

    Returns:
        {"{alignment}_{size}": (delta_mean, ci_lower, ci_upper)}
        e.g. "ppo_1.4b", "dpo_2.8b", "sft_6.9b"
    """
    results = {}

    for alignment in alignments:
        for i, size in enumerate(sizes):
            base_key = f"pythia-{size}-base"
            aligned_key = f"pythia-{size}-{alignment}"

            if base_key not in logprob_matrices:
                logger.warning("Missing base key: %s, skipping", base_key)
                continue
            if aligned_key not in logprob_matrices:
                logger.warning("Missing aligned key: %s, skipping", aligned_key)
                continue

            base_logprobs = logprob_matrices[base_key]
            aligned_logprobs = logprob_matrices[aligned_key]

            # Use different seed per pair for independence
            pair_seed = seed + i + alignments.index(alignment) * len(sizes)

            delta_mean, ci_lower, ci_upper = compute_delta_margin(
                base_logprobs=base_logprobs,
                aligned_logprobs=aligned_logprobs,
                n_bootstrap=n_bootstrap,
                seed=pair_seed,
            )

            key = f"{alignment}_{size}"
            results[key] = (delta_mean, ci_lower, ci_upper)
            logger.info(
                "  %s: Δmargin=%.4f [CI: %.4f, %.4f]",
                key, delta_mean, ci_lower, ci_upper
            )

    return results


def verify_mechanism_activated(results_dict: dict) -> tuple:
    """Verify shape, positive margins, delta computed for all 9 pairs.

    Args:
        results_dict: output from compute_all_delta_margins

    Returns:
        (mechanism_verified: bool, indicators: dict)
        indicators keys:
            logprob_matrix_shape_ok, margins_positive, delta_computed,
            delta_positive_ppo_count, ci_lower_positive_ppo_count
    """
    indicators = {
        "logprob_matrix_shape_ok": True,    # Verified in load_data
        "margins_positive": True,            # Enforced by assertions in compute_logit_margins
        "delta_computed": len(results_dict) == 9,
        "delta_positive_ppo_count": 0,
        "ci_lower_positive_ppo_count": 0,
    }

    if len(results_dict) == 0:
        indicators["delta_computed"] = False
        return False, indicators

    # Count PPO sizes with positive delta
    ppo_positive_delta = 0
    ppo_positive_ci = 0
    for key, (delta_mean, ci_lower, ci_upper) in results_dict.items():
        if key.startswith("ppo_"):
            if delta_mean > 0:
                ppo_positive_delta += 1
            if ci_lower > 0:
                ppo_positive_ci += 1

    indicators["delta_positive_ppo_count"] = ppo_positive_delta
    indicators["ci_lower_positive_ppo_count"] = ppo_positive_ci

    mechanism_verified = (
        indicators["delta_computed"] and
        indicators["logprob_matrix_shape_ok"] and
        indicators["margins_positive"]
    )

    return mechanism_verified, indicators


def test_gradient_ordering(
    delta_ppo: list,
    delta_dpo: list,
    delta_sft: list,
) -> dict:
    """Wilcoxon signed-rank one-sided tests across 3 Pythia sizes.

    Tests:
        H1: PPO >= DPO (one-sided, alternative='greater')
        H2: DPO > SFT  (one-sided, alternative='greater')

    Falls back to NaN if scipy raises ValueError (ties/zeros with n=3).

    Args:
        delta_ppo: [Δmargin_ppo_1.4b, Δmargin_ppo_2.8b, Δmargin_ppo_6.9b]
        delta_dpo: same for DPO
        delta_sft: same for SFT

    Returns:
        {ppo_ge_dpo_stat, ppo_ge_dpo_p, dpo_gt_sft_stat, dpo_gt_sft_p}
    """
    result = {
        "ppo_ge_dpo_stat": float("nan"),
        "ppo_ge_dpo_p": float("nan"),
        "dpo_gt_sft_stat": float("nan"),
        "dpo_gt_sft_p": float("nan"),
    }

    # Test 1: PPO >= DPO
    try:
        diff_ppo_dpo = [p - d for p, d in zip(delta_ppo, delta_dpo)]
        stat, p = stats.wilcoxon(diff_ppo_dpo, alternative="greater")
        result["ppo_ge_dpo_stat"] = float(stat)
        result["ppo_ge_dpo_p"] = float(p)
        logger.info("Wilcoxon PPO>=DPO: stat=%.4f, p=%.4f", stat, p)
    except ValueError as e:
        logger.warning("Wilcoxon PPO>=DPO failed (n=3, ties?): %s → NaN", e)

    # Test 2: DPO > SFT
    try:
        diff_dpo_sft = [d - s for d, s in zip(delta_dpo, delta_sft)]
        stat, p = stats.wilcoxon(diff_dpo_sft, alternative="greater")
        result["dpo_gt_sft_stat"] = float(stat)
        result["dpo_gt_sft_p"] = float(p)
        logger.info("Wilcoxon DPO>SFT: stat=%.4f, p=%.4f", stat, p)
    except ValueError as e:
        logger.warning("Wilcoxon DPO>SFT failed (n=3, ties?): %s → NaN", e)

    return result
