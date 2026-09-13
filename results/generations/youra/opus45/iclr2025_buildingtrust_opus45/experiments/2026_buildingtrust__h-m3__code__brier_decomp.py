"""Brier score decomposition for margin-based analysis.

Implements Murphy (1973) decomposition adapted for binary classification
using margin values converted to pseudo-probabilities via sigmoid.

Original Murphy decomposition: BS = REL - RES + UNC
where REL=Reliability, RES=Resolution (Refinement), UNC=Uncertainty

Reference:
- Murphy, A.H. (1973). A New Vector Partition of the Probability Score.
  Journal of Applied Meteorology, 12(4), 595-600.
"""
import numpy as np
from typing import Optional

from config import SEED, BOOTSTRAP_N, N_BINS, DECOMP_TOLERANCE


def margin_to_confidence(margins: np.ndarray) -> np.ndarray:
    """Convert margins to confidence scores via sigmoid.

    For multiple choice QA, margin = logit(top_choice) - logit(second_choice).
    Confidence P(correct) ≈ sigmoid(margin / temperature).

    Using temperature=1.0 gives standard sigmoid.

    Args:
        margins: (N,) array of margin values

    Returns:
        (N,) array of confidence values in [0, 1]
    """
    # Clip to prevent overflow
    margins_clipped = np.clip(margins, -20, 20)
    return 1 / (1 + np.exp(-margins_clipped))


def murphy_brier_decomposition(
    confidences: np.ndarray,
    correctness: np.ndarray,
    n_bins: int = N_BINS,
) -> dict[str, float]:
    """Murphy (1973) Brier decomposition for binary classification.

    Decomposes Brier Score into:
    - Reliability (REL): Calibration error - lower is better
    - Resolution (RES): Discrimination ability - higher is better
    - Uncertainty (UNC): Inherent data uncertainty - constant given base rate

    Formula: BS = REL - RES + UNC

    Args:
        confidences: (N,) predicted probabilities of correct answer
        correctness: (N,) binary labels (1=correct, 0=incorrect)
        n_bins: Number of bins for calibration curve

    Returns:
        Dictionary with keys:
            - brier_score: Overall Brier score
            - reliability: Calibration error component
            - resolution: Discrimination component (also called refinement)
            - uncertainty: Base rate entropy
            - refinement: Alias for resolution

    Raises:
        ValueError: If decomposition verification fails
    """
    N = len(confidences)
    assert len(correctness) == N, "Shape mismatch"

    # Ensure types
    confidences = np.asarray(confidences, dtype=np.float64)
    correctness = np.asarray(correctness, dtype=np.float64)

    # Brier score = mean squared error
    brier_score = np.mean((confidences - correctness) ** 2)

    # Base rate
    y_bar = np.mean(correctness)

    # Uncertainty = y_bar * (1 - y_bar)
    uncertainty = y_bar * (1 - y_bar)

    # Bin samples by predicted confidence
    bin_edges = np.linspace(0, 1, n_bins + 1)
    bin_indices = np.digitize(confidences, bin_edges[1:-1])

    reliability = 0.0
    resolution = 0.0

    for k in range(n_bins):
        mask = (bin_indices == k)
        n_k = np.sum(mask)

        if n_k == 0:
            continue

        # Mean predicted probability in bin k
        f_k = np.mean(confidences[mask])

        # Mean observed frequency in bin k
        o_k = np.mean(correctness[mask])

        # Reliability: sum over k of (n_k/N) * (f_k - o_k)^2
        reliability += (n_k / N) * (f_k - o_k) ** 2

        # Resolution: sum over k of (n_k/N) * (o_k - y_bar)^2
        resolution += (n_k / N) * (o_k - y_bar) ** 2

    # Verify decomposition: BS = REL - RES + UNC
    reconstructed = reliability - resolution + uncertainty
    diff = abs(brier_score - reconstructed)

    if diff > DECOMP_TOLERANCE:
        raise ValueError(
            f"Decomposition verification failed: "
            f"BS={brier_score:.6f}, REL-RES+UNC={reconstructed:.6f}, diff={diff:.6f}"
        )

    return {
        "brier_score": brier_score,
        "reliability": reliability,
        "resolution": resolution,
        "uncertainty": uncertainty,
        "refinement": resolution,  # Alias
    }


def bootstrap_decomposition(
    confidences: np.ndarray,
    correctness: np.ndarray,
    n_iterations: int = BOOTSTRAP_N,
    n_bins: int = N_BINS,
    seed: int = SEED,
) -> dict[str, np.ndarray]:
    """Bootstrap Brier decomposition for confidence intervals.

    Args:
        confidences: (N,) predicted probabilities
        correctness: (N,) binary labels
        n_iterations: Number of bootstrap iterations
        n_bins: Number of bins for calibration
        seed: Random seed for reproducibility

    Returns:
        Dictionary mapping component name -> (n_iterations,) array of values
    """
    N = len(confidences)
    rng = np.random.RandomState(seed)

    components = ["brier_score", "reliability", "resolution", "uncertainty", "refinement"]
    results = {c: np.zeros(n_iterations) for c in components}

    for i in range(n_iterations):
        # Bootstrap sample with replacement
        idx = rng.choice(N, size=N, replace=True)
        conf_boot = confidences[idx]
        corr_boot = correctness[idx]

        try:
            decomp = murphy_brier_decomposition(conf_boot, corr_boot, n_bins)
            for c in components:
                results[c][i] = decomp[c]
        except ValueError:
            # Decomposition failed for this sample, use NaN
            for c in components:
                results[c][i] = np.nan

    return results


def compute_ci(
    bootstrap_values: np.ndarray,
    alpha: float = 0.05,
) -> tuple[float, float, float]:
    """Compute confidence interval from bootstrap samples.

    Args:
        bootstrap_values: (n_iterations,) array of bootstrap estimates
        alpha: Significance level (default 0.05 for 95% CI)

    Returns:
        Tuple of (mean, ci_lower, ci_upper)
    """
    # Remove NaN values
    valid = bootstrap_values[~np.isnan(bootstrap_values)]

    if len(valid) == 0:
        return np.nan, np.nan, np.nan

    mean = np.mean(valid)
    ci_lower = np.percentile(valid, 100 * alpha / 2)
    ci_upper = np.percentile(valid, 100 * (1 - alpha / 2))

    return mean, ci_lower, ci_upper
