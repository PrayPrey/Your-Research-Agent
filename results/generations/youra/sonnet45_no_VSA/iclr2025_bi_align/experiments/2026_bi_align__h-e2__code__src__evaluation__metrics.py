"""Metrics evaluation for SAT profiling experiment."""

from typing import List, Tuple, Dict
import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix


def compute_degradation(epoch_time: float, baseline_time: float) -> float:
    """
    Compute degradation percentage.

    Args:
        epoch_time: Measured epoch time
        baseline_time: Baseline epoch time

    Returns:
        Degradation as fraction (0.15 = 15%)
    """
    if baseline_time == 0:
        return 0.0

    return (epoch_time - baseline_time) / baseline_time


def compute_precision_recall(
    SAT_values: List[float],
    degradations: List[float],
    threshold: float = 1.5
) -> Tuple[float, float, float]:
    """
    Compute precision, recall, and F1 score for degradation prediction.

    Args:
        SAT_values: List of SAT measurements
        degradations: List of degradation percentages
        threshold: SAT threshold for prediction (default: 1.5)

    Returns:
        Tuple of (precision, recall, f1_score)
    """
    # Binary classification: ≥15% degradation (positive class)
    y_true = [1 if d >= 0.15 else 0 for d in degradations]
    y_pred = [1 if s > threshold else 0 for s in SAT_values]

    # Handle edge case: no positive predictions
    if sum(y_pred) == 0:
        precision = 0.0
        recall = recall_score(y_true, y_pred, zero_division=0)
        f1 = 0.0
    else:
        precision = precision_score(y_true, y_pred, zero_division=0)
        recall = recall_score(y_true, y_pred, zero_division=0)
        f1 = f1_score(y_true, y_pred, zero_division=0)

    return precision, recall, f1


def compute_confusion_matrix(
    SAT_values: List[float],
    degradations: List[float],
    threshold: float = 1.5
) -> np.ndarray:
    """
    Compute confusion matrix.

    Args:
        SAT_values: List of SAT measurements
        degradations: List of degradation percentages
        threshold: SAT threshold for prediction

    Returns:
        2x2 confusion matrix [[TN, FP], [FN, TP]]
    """
    y_true = [1 if d >= 0.15 else 0 for d in degradations]
    y_pred = [1 if s > threshold else 0 for s in SAT_values]

    return confusion_matrix(y_true, y_pred)


def evaluate_causality(
    SAT_natural: float,
    SAT_jitter: Dict[int, float],
    gpu_util: float
) -> Dict[str, float]:
    """
    Validate causality: SAT should increase with jitter delay.

    Args:
        SAT_natural: SAT without jitter (0ms delay)
        SAT_jitter: Dictionary mapping delay_ms -> SAT value
        gpu_util: Average GPU utilization (0-100)

    Returns:
        Dictionary with correlation and conditional effect metrics
    """
    # Extract delays and SAT values
    delays = sorted(SAT_jitter.keys())
    sat_values = [SAT_jitter[d] for d in delays]

    # Compute correlation
    if len(delays) > 1:
        correlation = np.corrcoef(delays, sat_values)[0, 1]
    else:
        correlation = 0.0

    # Check if SAT increases monotonically
    monotonic_increase = all(sat_values[i] <= sat_values[i + 1] for i in range(len(sat_values) - 1))

    # Conditional effect: SAT increase should be stronger when GPU util < 90%
    conditional_effect = 1.0 if gpu_util < 90 else 0.5

    return {
        "correlation": correlation,
        "monotonic_increase": monotonic_increase,
        "conditional_effect": conditional_effect,
        "causality_validated": correlation > 0.7 and monotonic_increase
    }


def compute_precision_recall_curve(
    SAT_values: List[float],
    degradations: List[float],
    thresholds: List[float] = None
) -> Tuple[List[float], List[float], List[float]]:
    """
    Compute precision-recall curve by varying SAT threshold.

    Args:
        SAT_values: List of SAT measurements
        degradations: List of degradation percentages
        thresholds: List of SAT thresholds to evaluate (default: 1.0 to 2.5)

    Returns:
        Tuple of (thresholds, precisions, recalls)
    """
    if thresholds is None:
        thresholds = np.linspace(1.0, 2.5, 30).tolist()

    precisions = []
    recalls = []

    for threshold in thresholds:
        precision, recall, _ = compute_precision_recall(SAT_values, degradations, threshold)
        precisions.append(precision)
        recalls.append(recall)

    return thresholds, precisions, recalls
