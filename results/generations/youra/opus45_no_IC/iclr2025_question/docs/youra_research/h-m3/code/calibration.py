"""Threshold calibration and transfer evaluation for H-M3."""

import numpy as np
from sklearn.metrics import roc_curve, roc_auc_score
from config import TARGET_FPR


def calibrate_threshold(entropies: np.ndarray, labels: np.ndarray, target_fpr: float = TARGET_FPR) -> float:
    """Find threshold at target FPR.

    Higher entropy = more likely hallucination.
    labels=True means correct response.
    """
    y_true = ~labels.astype(bool)
    fpr, tpr, thresholds = roc_curve(y_true, entropies)
    idx = np.argmin(np.abs(fpr - target_fpr))
    return float(thresholds[idx])


def evaluate_transfer(source_threshold: float, target_entropies: np.ndarray, target_labels: np.ndarray) -> dict:
    """Evaluate AUROC using source-calibrated threshold on target data."""
    y_true = ~target_labels.astype(bool)
    auroc = roc_auc_score(y_true, target_entropies)
    return {"auroc": float(auroc), "threshold_used": source_threshold}


def compute_auroc_degradation(source_auroc: float, target_auroc: float) -> float:
    """Positive = performance dropped."""
    return source_auroc - target_auroc
