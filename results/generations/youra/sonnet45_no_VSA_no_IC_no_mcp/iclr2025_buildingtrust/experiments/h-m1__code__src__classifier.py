"""Threshold-based binary classifier."""
import numpy as np
from sklearn.metrics import accuracy_score
from typing import Tuple, List


class ThresholdClassifier:
    """Binary classifier using single threshold on entropy values."""

    def __init__(self, threshold: float = 0.5):
        """Initialize with default threshold."""
        self.threshold = threshold
        self.best_threshold: float = 0.5
        self.train_accuracy: float = 0.0

    def fit(self, X_train: np.ndarray, y_train: np.ndarray,
            thresholds: np.ndarray) -> Tuple[float, List[float], List[float]]:
        """Grid search optimal threshold. X_train: (N,), y_train: (N,). Returns: (best_threshold, threshold_list, accuracy_list)"""
        best_acc = 0.0
        threshold_list = []
        accuracy_list = []

        for threshold in thresholds:
            # Rule: entropy < threshold -> entity-error (0), else non-entity-error (1)
            preds = (X_train >= threshold).astype(int)
            acc = accuracy_score(y_train, preds)

            threshold_list.append(threshold)
            accuracy_list.append(acc)

            if acc > best_acc:
                best_acc = acc
                self.best_threshold = threshold
                self.train_accuracy = acc

        return self.best_threshold, threshold_list, accuracy_list

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Apply threshold. X: (N,) -> (N,) binary predictions. Rule: entropy < threshold -> 0 (entity-error)"""
        return (X >= self.best_threshold).astype(int)

    def get_threshold(self) -> float:
        """Return fitted threshold."""
        return self.best_threshold
