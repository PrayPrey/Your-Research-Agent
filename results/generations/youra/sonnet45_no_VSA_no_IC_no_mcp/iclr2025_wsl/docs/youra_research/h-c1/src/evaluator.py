"""Evaluation metrics for boundary detection."""

from typing import Dict, List
import numpy as np


class BoundaryEvaluator:
    """Compute boundary detection metrics."""

    def __init__(self, gate_threshold: float = 0.80):
        self.gate_threshold = gate_threshold

    def evaluate_boundary_detection(self, predictions: List[bool], ground_truth: List[bool]) -> Dict:
        """Compute accuracy, precision, recall, F1.

        Args:
            predictions: List of testable predictions (True = testable, False = not_testable)
            ground_truth: List of expected labels (False = boundary case)

        Returns:
            {accuracy, precision, recall, f1, gate_passed}
        """
        predictions = np.array(predictions)
        ground_truth = np.array(ground_truth)

        # For boundary detection:
        # TP: Correctly flagged as not_testable (prediction=False, truth=False)
        # TN: Correctly flagged as testable (prediction=True, truth=True)
        # FP: Incorrectly flagged as not_testable (prediction=False, truth=True)
        # FN: Missed boundary case (prediction=True, truth=False)

        # Convert to binary: 1 = boundary (not_testable), 0 = in-scope (testable)
        pred_boundary = ~predictions  # False -> 1, True -> 0
        true_boundary = ~ground_truth

        tp = np.sum(pred_boundary & true_boundary)
        tn = np.sum(~pred_boundary & ~true_boundary)
        fp = np.sum(pred_boundary & ~true_boundary)
        fn = np.sum(~pred_boundary & true_boundary)

        accuracy = (tp + tn) / len(predictions) if len(predictions) > 0 else 0.0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

        gate_passed = accuracy >= self.gate_threshold

        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'tp': int(tp),
            'tn': int(tn),
            'fp': int(fp),
            'fn': int(fn),
            'gate_passed': gate_passed
        }
