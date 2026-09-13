"""Precision/recall evaluator for binary classification."""
from typing import Dict, List
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix, classification_report


class PrecisionRecallEvaluator:
    def compute_metrics(self, y_true: List[int], y_pred: List[int]) -> Dict[str, float]:
        """
        Compute binary classification metrics.

        Args:
            y_true: Ground truth labels [0 or 1]
            y_pred: Predicted labels [0 or 1]

        Returns:
            Dict with keys: precision, recall, f1, tp, fp, tn, fn
        """
        precision = precision_score(y_true, y_pred, zero_division=0)
        recall = recall_score(y_true, y_pred, zero_division=0)
        f1 = f1_score(y_true, y_pred, zero_division=0)

        cm = confusion_matrix(y_true, y_pred)
        tn, fp, fn, tp = cm.ravel() if cm.size == 4 else (0, 0, 0, 0)

        return {
            'precision': float(precision),
            'recall': float(recall),
            'f1': float(f1),
            'tp': int(tp),
            'fp': int(fp),
            'tn': int(tn),
            'fn': int(fn)
        }

    def generate_classification_report(
        self, y_true: List[int], y_pred: List[int]
    ) -> str:
        """
        Generate sklearn classification report.

        Args:
            y_true: Ground truth labels
            y_pred: Predicted labels

        Returns:
            Classification report string
        """
        return classification_report(
            y_true, y_pred,
            target_names=['No Shift', 'Shift'],
            zero_division=0
        )
