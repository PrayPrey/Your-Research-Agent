"""
argmax_partition.py — H-M3 Mechanism Discrimination
Shared/changed-argmax partition, per-subset Brier reliability, Cohen's d.
"""
import logging
import sys
from pathlib import Path

import numpy as np
from scipy.special import softmax

# Add h-e1/code to path
_CODE_DIR = Path(__file__).parent.resolve()
_H_E1_CODE_DIR = str(_CODE_DIR.parent.parent / "h-e1" / "code")
if _H_E1_CODE_DIR not in sys.path:
    sys.path.insert(0, _H_E1_CODE_DIR)

from calibration_analysis import compute_brier_decomposition  # noqa: E402

logger = logging.getLogger(__name__)


def partition_items_by_argmax(
    base_logprobs: np.ndarray,
    aligned_logprobs: np.ndarray,
) -> tuple:
    """Partition N MMLU items into shared/changed-argmax subsets.

    Args:
        base_logprobs: (N, 4) float64
        aligned_logprobs: (N, 4) float64

    Returns:
        shared_mask: (N,) bool — argmax unchanged
        changed_mask: (N,) bool — argmax changed
    """
    base_argmax = np.argmax(base_logprobs, axis=1)
    aligned_argmax = np.argmax(aligned_logprobs, axis=1)
    shared_mask = base_argmax == aligned_argmax
    changed_mask = ~shared_mask
    return shared_mask, changed_mask


def compute_brier_reliability_subset(
    probs: np.ndarray,
    labels: np.ndarray,
    mask: np.ndarray,
    n_bins: int = 15,
) -> float:
    """Brier reliability (Murphy 1973) for a masked subset.

    Args:
        probs: (N, 4) softmax probabilities
        labels: (N,) int64
        mask: (N,) bool

    Returns:
        reliability float (0 if no samples in mask)
    """
    if mask.sum() == 0:
        return 0.0

    probs_sub = probs[mask]
    labels_sub = labels[mask]
    decomp = compute_brier_decomposition(labels_sub, probs_sub, n_bins=n_bins)
    # compute_brier_decomposition returns (reliability, resolution, uncertainty)
    if isinstance(decomp, (tuple, list)):
        return float(decomp[0])
    elif isinstance(decomp, dict):
        return float(decomp.get("reliability", decomp.get("REL", 0.0)))
    return float(decomp)


def compute_cohens_d(
    group1: np.ndarray,
    group2: np.ndarray,
) -> float:
    """Cohen's d effect size: (mean1 - mean2) / pooled_std."""
    n1, n2 = len(group1), len(group2)
    if n1 < 2 or n2 < 2:
        return 0.0
    mean_diff = np.mean(group1) - np.mean(group2)
    pooled_std = np.sqrt(
        ((n1 - 1) * np.var(group1, ddof=1) + (n2 - 1) * np.var(group2, ddof=1))
        / (n1 + n2 - 2)
    )
    if pooled_std == 0.0:
        return 0.0
    return float(mean_diff / pooled_std)


def compute_all_partition_results(
    logprob_matrices: dict,
    labels: dict,
    sizes: list,
    alignments: list,
    n_bootstrap: int = 1000,
    seed: int = 42,
) -> dict:
    """Compute shared/changed-argmax Brier partition for all 9 pairs.

    Returns:
        {'{size}-{alignment}': {
            'shared_mask', 'changed_mask',
            'n_shared', 'n_changed',
            'rel_shared_base', 'rel_shared_aligned',
            'rel_changed_base', 'rel_changed_aligned',
            'cohens_d_shared',
            'h1_signature', 'h2_check',
        }}
    """
    from config import H1_COHENS_D_THRESHOLD, N_BINS

    rng = np.random.default_rng(seed)
    results = {}

    for size in sizes:
        base_key = f"pythia-{size}-base"
        base_lp = logprob_matrices.get(base_key)
        y_true = labels.get(base_key)
        if base_lp is None or y_true is None:
            logger.warning("Missing base data for size %s", size)
            continue

        for alignment in alignments:
            aligned_key = f"pythia-{size}-{alignment}"
            aligned_lp = logprob_matrices.get(aligned_key)
            if aligned_lp is None:
                logger.warning("Missing aligned data for %s", aligned_key)
                continue

            n = min(base_lp.shape[0], aligned_lp.shape[0], len(y_true))
            base_sub = base_lp[:n]
            aligned_sub = aligned_lp[:n]
            labels_sub = y_true[:n]

            shared_mask, changed_mask = partition_items_by_argmax(base_sub, aligned_sub)

            # Softmax probabilities
            base_probs = softmax(base_sub, axis=1)
            aligned_probs = softmax(aligned_sub, axis=1)

            rel_shared_base = compute_brier_reliability_subset(
                base_probs, labels_sub, shared_mask, N_BINS
            )
            rel_shared_aligned = compute_brier_reliability_subset(
                aligned_probs, labels_sub, shared_mask, N_BINS
            )
            rel_changed_base = compute_brier_reliability_subset(
                base_probs, labels_sub, changed_mask, N_BINS
            )
            rel_changed_aligned = compute_brier_reliability_subset(
                aligned_probs, labels_sub, changed_mask, N_BINS
            )

            # Cohen's d: shared vs changed Brier reliability difference
            # Use bootstrap to get per-bootstrap reliability values
            shared_rel_vals = []
            changed_rel_vals = []
            indices = np.arange(n)
            for _ in range(n_bootstrap):
                boot_idx = rng.choice(indices, size=n, replace=True)
                boot_shared = shared_mask[boot_idx]
                boot_changed = changed_mask[boot_idx]
                boot_base_probs = base_probs[boot_idx]
                boot_labels = labels_sub[boot_idx]
                s_val = compute_brier_reliability_subset(boot_base_probs, boot_labels, boot_shared, N_BINS)
                c_val = compute_brier_reliability_subset(boot_base_probs, boot_labels, boot_changed, N_BINS)
                shared_rel_vals.append(s_val)
                changed_rel_vals.append(c_val)

            cohens_d_shared = compute_cohens_d(
                np.array(shared_rel_vals), np.array(changed_rel_vals)
            )

            # H1 signature: shared-argmax items show higher reliability than changed
            h1_signature = (rel_shared_aligned > rel_changed_aligned) and (
                abs(cohens_d_shared) < H1_COHENS_D_THRESHOLD
            )
            # H2 check: large effect in changed-argmax items (boundary shift)
            h2_check = rel_changed_aligned > rel_shared_aligned

            pair_key = f"{size}-{alignment}"
            results[pair_key] = {
                "shared_mask": shared_mask,
                "changed_mask": changed_mask,
                "n_shared": int(shared_mask.sum()),
                "n_changed": int(changed_mask.sum()),
                "rel_shared_base": rel_shared_base,
                "rel_shared_aligned": rel_shared_aligned,
                "rel_changed_base": rel_changed_base,
                "rel_changed_aligned": rel_changed_aligned,
                "cohens_d_shared": cohens_d_shared,
                "h1_signature": h1_signature,
                "h2_check": h2_check,
            }
            logger.info(
                "Partition %s: n_shared=%d n_changed=%d cohens_d=%.4f h1_sig=%s",
                pair_key, shared_mask.sum(), changed_mask.sum(),
                cohens_d_shared, h1_signature,
            )

    return results
