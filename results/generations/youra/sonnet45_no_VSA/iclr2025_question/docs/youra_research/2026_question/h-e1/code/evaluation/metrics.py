"""
Metrics computation for CCP ρ_j and secondary metrics.
"""

import numpy as np
from scipy.stats import pearsonr, wilcoxon
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


def compute_rho_j(nli_scores: np.ndarray, epsilon: float = 1e-8) -> float:
    """
    Compute CCP ρ_j metric for a single sample.

    ρ_j = median((contradict_mass + entail_mass) / total_mass)

    Args:
        nli_scores: (N_claims, 3) array [contradiction, entailment, neutral]
        epsilon: Small value to prevent division by zero

    Returns:
        rho_j: median claim-type mass ratio
    """
    if len(nli_scores) == 0:
        return 0.0

    # Extract contradiction and entailment masses
    contradict_mass = nli_scores[:, 0]  # First column
    entail_mass = nli_scores[:, 1]      # Second column
    # neutral_mass = nli_scores[:, 2]   # Third column (not used in numerator)

    # Total mass for each claim
    total_mass = nli_scores.sum(axis=1) + epsilon

    # Claim-type mass ratio for each claim
    claim_type_ratios = (contradict_mass + entail_mass) / total_mass

    # Return median across all claims
    rho_j = np.median(claim_type_ratios)

    return float(rho_j)


def compute_autocorrelation(scores: np.ndarray, max_lag: int = 10) -> List[float]:
    """
    Compute autocorrelation for lags 1 to max_lag.

    Args:
        scores: (N,) array of CCP scores
        max_lag: Maximum lag

    Returns:
        autocorr: List of autocorrelation coefficients
    """
    if len(scores) < 2:
        return [0.0] * max_lag

    autocorr = []
    for lag in range(1, max_lag + 1):
        if len(scores) <= lag:
            autocorr.append(0.0)
            continue

        try:
            corr, _ = pearsonr(scores[:-lag], scores[lag:])
            autocorr.append(float(corr) if not np.isnan(corr) else 0.0)
        except Exception as e:
            logger.warning(f"Autocorrelation computation failed at lag {lag}: {e}")
            autocorr.append(0.0)

    return autocorr


def compute_krippendorff_alpha(decompositions: List[List[str]]) -> float:
    """
    Compute claim decomposition reliability using Krippendorff's alpha.

    Args:
        decompositions: List of 2 decompositions for same texts

    Returns:
        alpha: Krippendorff's alpha coefficient
    """
    # For PoC: simplified reliability measure
    # In production, would use actual Krippendorff's alpha implementation
    # Here we approximate with overlap-based agreement

    if len(decompositions) < 2:
        logger.warning("Need at least 2 decompositions for reliability measure")
        return 0.0

    agreements = []
    for i in range(len(decompositions[0])):
        if i >= len(decompositions[1]):
            break

        # Count overlap in number of claims as a proxy
        n_claims_1 = len(decompositions[0][i])
        n_claims_2 = len(decompositions[1][i])

        if n_claims_1 == 0 or n_claims_2 == 0:
            continue

        # Agreement based on claim count similarity
        agreement = 1.0 - abs(n_claims_1 - n_claims_2) / max(n_claims_1, n_claims_2)
        agreements.append(agreement)

    if not agreements:
        return 0.0

    return float(np.mean(agreements))


def statistical_test(
    factual_rho: np.ndarray,
    creative_rho: np.ndarray
) -> Dict[str, float]:
    """
    Run statistical test for ρ_j degradation.

    Args:
        factual_rho: (N,) array of factual domain ρ_j values
        creative_rho: (N,) array of creative domain ρ_j values

    Returns:
        {
            "delta_rho_j": float,
            "median_factual": float,
            "median_creative": float,
            "p_value": float,
            "effect_size": float
        }
    """
    median_factual = np.median(factual_rho)
    median_creative = np.median(creative_rho)
    delta_rho_j = median_creative - median_factual

    # Wilcoxon signed-rank test (paired samples)
    try:
        # Pad to same length if needed
        min_len = min(len(factual_rho), len(creative_rho))
        stat, p_value = wilcoxon(
            creative_rho[:min_len],
            factual_rho[:min_len],
            alternative='greater'
        )
    except Exception as e:
        logger.warning(f"Statistical test failed: {e}")
        p_value = 1.0

    # Effect size (Cohen's d approximation)
    pooled_std = np.sqrt((np.std(factual_rho)**2 + np.std(creative_rho)**2) / 2)
    effect_size = delta_rho_j / pooled_std if pooled_std > 0 else 0.0

    return {
        "delta_rho_j": float(delta_rho_j),
        "median_factual": float(median_factual),
        "median_creative": float(median_creative),
        "p_value": float(p_value),
        "effect_size": float(effect_size)
    }
