"""ValidationMetrics: Accuracy, precision, recall, confusion matrix via sklearn."""

from typing import Dict, List, Any, Set
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
import numpy as np


class ValidationMetrics:
    """Compute validation metrics for token-level execution classification."""

    def __init__(self):
        pass

    def token_accuracy(self, pred_mask: List[int], gt_mask: List[int]) -> float:
        """Compute accuracy of token classification."""
        if len(pred_mask) != len(gt_mask):
            min_len = min(len(pred_mask), len(gt_mask))
            pred_mask = pred_mask[:min_len]
            gt_mask = gt_mask[:min_len]

        if not pred_mask:
            return 0.0

        return accuracy_score(gt_mask, pred_mask)

    def precision_recall(self, pred_mask: List[int], gt_mask: List[int]) -> Dict[str, float]:
        """Compute precision, recall, F1 for executed tokens (class 1)."""
        if len(pred_mask) != len(gt_mask):
            min_len = min(len(pred_mask), len(gt_mask))
            pred_mask = pred_mask[:min_len]
            gt_mask = gt_mask[:min_len]

        if not pred_mask or sum(gt_mask) == 0:
            return {"precision": 0.0, "recall": 0.0, "f1": 0.0}

        prec, rec, f1, _ = precision_recall_fscore_support(
            gt_mask, pred_mask, average="binary", zero_division=0
        )

        return {
            "precision": float(prec),
            "recall": float(rec),
            "f1": float(f1)
        }

    def line_coverage_accuracy(self, pred_lines: Set[int], gt_lines: Set[int]) -> float:
        """Compute accuracy at line level."""
        if not gt_lines:
            return 1.0 if not pred_lines else 0.0

        if not pred_lines:
            return 0.0

        all_lines = pred_lines | gt_lines
        correct = len(pred_lines & gt_lines) + len(all_lines - pred_lines - gt_lines)

        return len(pred_lines & gt_lines) / len(gt_lines)

    def compute_confusion_matrix(self, pred_mask: List[int], gt_mask: List[int]) -> np.ndarray:
        """Compute 2x2 confusion matrix."""
        if len(pred_mask) != len(gt_mask):
            min_len = min(len(pred_mask), len(gt_mask))
            pred_mask = pred_mask[:min_len]
            gt_mask = gt_mask[:min_len]

        if not pred_mask:
            return np.array([[0, 0], [0, 0]])

        return confusion_matrix(gt_mask, pred_mask, labels=[0, 1])

    def compute_all(
        self,
        pred_mask: List[int],
        gt_mask: List[int],
        pred_lines: Set[int] = None,
        gt_lines: Set[int] = None
    ) -> Dict[str, Any]:
        """Compute all metrics."""
        result = {
            "token_accuracy": self.token_accuracy(pred_mask, gt_mask),
            **self.precision_recall(pred_mask, gt_mask),
            "confusion_matrix": self.compute_confusion_matrix(pred_mask, gt_mask).tolist()
        }

        if pred_lines is not None and gt_lines is not None:
            result["line_coverage_accuracy"] = self.line_coverage_accuracy(pred_lines, gt_lines)

        return result
