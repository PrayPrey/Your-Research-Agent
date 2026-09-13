"""Evaluation: correlations and distinctness verification."""

import numpy as np
from scipy.stats import pearsonr, spearmanr, kendalltau


def compute_method_correlations(scores_dict):
    """
    Compute pairwise correlations between attribution methods.
    scores_dict[method] shape: (num_test, num_train)
    Returns: dict of correlations per pair.
    """
    methods = list(scores_dict.keys())
    correlations = {}

    for i, m1 in enumerate(methods):
        for m2 in methods[i+1:]:
            s1 = scores_dict[m1].flatten()
            s2 = scores_dict[m2].flatten()

            # Handle potential NaN/Inf
            valid = np.isfinite(s1) & np.isfinite(s2)
            s1_valid, s2_valid = s1[valid], s2[valid]

            correlations[f'{m1}_vs_{m2}'] = {
                'pearson': float(pearsonr(s1_valid, s2_valid)[0]),
                'spearman': float(spearmanr(s1_valid, s2_valid)[0]),
                'kendall': float(kendalltau(s1_valid, s2_valid)[0]),
            }

    return correlations


def verify_mathematical_distinctness(scores_dict, threshold=0.9):
    """
    Verify that methods produce mathematically distinct outputs.
    Returns: (passed: bool, evidence: dict)
    """
    # Check for NaN/Inf
    for name, s in scores_dict.items():
        finite_ratio = np.isfinite(s).mean()
        if finite_ratio < 0.99:
            print(f"Warning: {name} has {(1-finite_ratio)*100:.2f}% non-finite values")

    correlations = compute_method_correlations(scores_dict)

    max_correlation = max(abs(c['pearson']) for c in correlations.values())
    passed = max_correlation < threshold

    evidence = {
        'max_correlation': float(max_correlation),
        'threshold': threshold,
        'all_correlations': correlations,
        'verdict': 'DISTINCT' if passed else 'TOO_SIMILAR',
        'gate_passed': passed,
    }

    return passed, evidence
