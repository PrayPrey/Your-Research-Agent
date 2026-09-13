"""Compute metrics and gate check."""
import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
from typing import Dict


class Evaluator:
    """Compute classification metrics and gate check."""

    def evaluate(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict:
        """Compute classification metrics. Returns: {accuracy, precision, recall, f1, confusion_matrix}"""
        precision, recall, f1, _ = precision_recall_fscore_support(
            y_true, y_pred, average='binary', zero_division=0
        )

        return {
            "accuracy": float(accuracy_score(y_true, y_pred)),
            "precision": float(precision),
            "recall": float(recall),
            "f1": float(f1),
            "confusion_matrix": confusion_matrix(y_true, y_pred).tolist()
        }

    def check_gate(self, accuracy: float, threshold: float = 0.70) -> bool:
        """Return True if accuracy >= threshold."""
        return accuracy >= threshold
