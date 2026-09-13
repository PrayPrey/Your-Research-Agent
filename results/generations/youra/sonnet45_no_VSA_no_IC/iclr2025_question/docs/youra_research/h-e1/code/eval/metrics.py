"""Evaluation metrics for selective prediction."""
from typing import List, Dict
from sklearn.metrics import roc_auc_score, roc_curve
from scipy.stats import spearmanr
import numpy as np


def compute_auroc(y_true: List[int], uncertainties: List[float]) -> float:
    """
    Compute AUROC for selective prediction.

    Args:
        y_true: Binary labels (0=correct, 1=incorrect)
        uncertainties: Uncertainty scores (higher = should abstain)

    Returns:
        AUROC score (0.5 to 1.0)
    """
    return roc_auc_score(y_true, uncertainties)


def compute_spearman(uncertainties: List[float], incorrectness: List[int]) -> float:
    """
    Compute Spearman correlation between uncertainty and incorrectness.

    Args:
        uncertainties: Uncertainty scores
        incorrectness: Binary incorrectness labels (0=correct, 1=incorrect)

    Returns:
        Spearman rho correlation coefficient
    """
    rho, _ = spearmanr(uncertainties, incorrectness)
    return rho


def check_gate(auroc_scores: Dict[str, float], threshold: float = 0.7) -> bool:
    """
    Check if any UQ method passes AUROC gate.

    Args:
        auroc_scores: {method_name: auroc} dictionary
        threshold: Minimum AUROC threshold (default 0.7)

    Returns:
        True if max(AUROC) >= threshold, False otherwise
    """
    max_auroc = max(auroc_scores.values())
    return max_auroc >= threshold


def compute_roc_data(y_true: List[int], uncertainties: List[float]) -> Dict:
    """
    Compute ROC curve data.

    Args:
        y_true: Binary labels
        uncertainties: Uncertainty scores

    Returns:
        {fpr: [...], tpr: [...], thresholds: [...]}
    """
    fpr, tpr, thresholds = roc_curve(y_true, uncertainties)
    return {"fpr": fpr.tolist(), "tpr": tpr.tolist(), "thresholds": thresholds.tolist()}
