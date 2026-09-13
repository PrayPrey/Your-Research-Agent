"""
spearman_analysis.py — H-M3 Mechanism Discrimination
Per-item Spearman rho between base and aligned log-prob vectors.
"""
import logging

import numpy as np
from scipy import stats

logger = logging.getLogger(__name__)


def compute_spearman_rho_per_item(
    base_logprobs: np.ndarray,
    aligned_logprobs: np.ndarray,
) -> tuple:
    """Per-item Spearman rho over 4-option log-prob vectors.

    Args:
        base_logprobs: (N, 4) float64
        aligned_logprobs: (N, 4) float64

    Returns:
        rho_per_item: (N,) float64
        mean_rho: float
    """
    N = base_logprobs.shape[0]
    rho_per_item = np.array([
        stats.spearmanr(base_logprobs[i], aligned_logprobs[i]).statistic
        for i in range(N)
    ], dtype=np.float64)
    mean_rho = float(np.nanmean(rho_per_item))
    return rho_per_item, mean_rho


def compute_all_spearman_results(
    logprob_matrices: dict,
    sizes: list,
    alignments: list,
) -> dict:
    """Compute Spearman rho for all 9 base-aligned pairs.

    Returns:
        {'{size}-{alignment}': {'rho_per_item': ndarray, 'mean_rho': float,
                                 'h1_pass': bool, 'h2_flag': bool}}
    """
    from config import H1_RHO_THRESHOLD, H2_RHO_THRESHOLD

    results = {}
    for size in sizes:
        base_key = f"pythia-{size}-base"
        base_lp = logprob_matrices.get(base_key)
        if base_lp is None:
            logger.warning("Base logprobs not found for size %s", size)
            continue
        for alignment in alignments:
            aligned_key = f"pythia-{size}-{alignment}"
            aligned_lp = logprob_matrices.get(aligned_key)
            if aligned_lp is None:
                logger.warning("Aligned logprobs not found for %s", aligned_key)
                continue

            # Align lengths
            n = min(base_lp.shape[0], aligned_lp.shape[0])
            rho_per_item, mean_rho = compute_spearman_rho_per_item(
                base_lp[:n], aligned_lp[:n]
            )
            pair_key = f"{size}-{alignment}"
            results[pair_key] = {
                "rho_per_item": rho_per_item,
                "mean_rho": mean_rho,
                "h1_pass": mean_rho >= H1_RHO_THRESHOLD,
                "h2_flag": mean_rho < H2_RHO_THRESHOLD,
            }
            logger.info(
                "Spearman rho %s: mean=%.4f h1_pass=%s h2_flag=%s",
                pair_key, mean_rho,
                results[pair_key]["h1_pass"],
                results[pair_key]["h2_flag"],
            )
    return results


def assess_h1_h2_gate(
    spearman_results: dict,
    h1_threshold: float = 0.9,
    h2_threshold: float = 0.85,
) -> dict:
    """Assess H1/H2 gate: all 9 pairs must pass H1.

    Returns:
        {'gate_pass': bool, 'n_h1_pass': int, 'n_h2_flag': int, 'per_pair': dict}
    """
    per_pair = {}
    n_h1_pass = 0
    n_h2_flag = 0

    for pair_key, res in spearman_results.items():
        mean_rho = res["mean_rho"]
        h1_pass = mean_rho >= h1_threshold
        h2_flag = mean_rho < h2_threshold
        per_pair[pair_key] = {"mean_rho": mean_rho, "h1_pass": h1_pass, "h2_flag": h2_flag}
        if h1_pass:
            n_h1_pass += 1
        if h2_flag:
            n_h2_flag += 1

    gate_pass = n_h1_pass == len(spearman_results) and len(spearman_results) > 0
    logger.info(
        "H1/H2 gate: gate_pass=%s n_h1_pass=%d/%d n_h2_flag=%d",
        gate_pass, n_h1_pass, len(spearman_results), n_h2_flag,
    )
    return {
        "gate_pass": gate_pass,
        "n_h1_pass": n_h1_pass,
        "n_h2_flag": n_h2_flag,
        "per_pair": per_pair,
    }
