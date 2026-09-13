"""Evaluation metrics: AUROC, permutation tests, Spearman correlation."""

import numpy as np
from typing import Tuple, Dict
from sklearn.metrics import roc_auc_score
from scipy.stats import spearmanr


def compute_auroc(y_true: np.ndarray, y_score: np.ndarray) -> float:
    """Compute AUROC.
    
    Args:
        y_true: Binary labels
        y_score: Predicted scores (higher = more confident)
        
    Returns:
        AUROC ∈ [0, 1]
    """
    return roc_auc_score(y_true, y_score)


def paired_permutation_test(
    auroc_a: float,
    auroc_b: float,
    scores_a: np.ndarray,
    scores_b: np.ndarray,
    y_true: np.ndarray,
    n_permutations: int = 10000,
    random_seed: int = 42
) -> float:
    """Paired permutation test for AUROC difference.
    
    Args:
        auroc_a: AUROC for method A
        auroc_b: AUROC for method B
        scores_a: Scores from method A
        scores_b: Scores from method B
        y_true: Ground truth labels
        n_permutations: Number of permutations
        random_seed: Random seed
        
    Returns:
        p-value
    """
    np.random.seed(random_seed)
    
    delta_obs = auroc_a - auroc_b
    
    perm_deltas = []
    for _ in range(n_permutations):
        # Random swap with p=0.5
        swap_mask = np.random.rand(len(scores_a)) < 0.5
        scores_a_perm = np.where(swap_mask, scores_b, scores_a)
        scores_b_perm = np.where(swap_mask, scores_a, scores_b)
        
        auroc_a_perm = roc_auc_score(y_true, scores_a_perm)
        auroc_b_perm = roc_auc_score(y_true, scores_b_perm)
        delta_k = auroc_a_perm - auroc_b_perm
        perm_deltas.append(delta_k)
    
    perm_deltas = np.array(perm_deltas)
    p_value = (perm_deltas >= delta_obs).sum() / n_permutations
    
    return p_value


def spearman_correlation(x: np.ndarray, y: np.ndarray) -> Tuple[float, float]:
    """Compute Spearman rank correlation.
    
    Args:
        x: First variable
        y: Second variable
        
    Returns:
        (rho, p_value)
    """
    rho, p_value = spearmanr(x, y)
    return rho, p_value


class StratumEval:
    """Evaluate uncertainty methods per stratum."""
    
    def __init__(self, se: np.ndarray, kle: np.ndarray, labels: np.ndarray):
        self.se = se
        self.kle = kle
        self.labels = labels
    
    def eval_stratum(self, mask: np.ndarray) -> Dict:
        """Evaluate on a specific stratum.
        
        Args:
            mask: Boolean mask for stratum
            
        Returns:
            Dictionary with auroc_se, auroc_kle, divergence, p_value
        """
        se_stratum = self.se[mask]
        kle_stratum = self.kle[mask]
        labels_stratum = self.labels[mask]
        
        # Negative entropy: lower = more confident
        auroc_se = compute_auroc(labels_stratum, -se_stratum)
        auroc_kle = compute_auroc(labels_stratum, -kle_stratum)
        
        # Permutation test
        p_value = paired_permutation_test(
            auroc_kle, auroc_se,
            -kle_stratum, -se_stratum,
            labels_stratum
        )
        
        return {
            'auroc_se': auroc_se,
            'auroc_kle': auroc_kle,
            'divergence': auroc_kle - auroc_se,
            'p_value': p_value,
            'n_samples': mask.sum()
        }
