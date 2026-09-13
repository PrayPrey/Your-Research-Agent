"""Metrics computation for confound detection."""

from typing import Dict, List


class Evaluator:
    """Calculate precision, recall, accuracy, F1."""

    @staticmethod
    def compute_metrics(y_true: List[str], y_pred: List[str]) -> Dict[str, float]:
        """Calculate precision, recall, accuracy, F1. Returns: metrics dict."""
        tp = sum(
            1 for t, p in zip(y_true, y_pred) if t == "confounded" and p == "confounded"
        )
        fp = sum(
            1
            for t, p in zip(y_true, y_pred)
            if t == "unconfounded" and p == "confounded"
        )
        tn = sum(
            1
            for t, p in zip(y_true, y_pred)
            if t == "unconfounded" and p == "unconfounded"
        )
        fn = sum(
            1 for t, p in zip(y_true, y_pred) if t == "confounded" and p == "unconfounded"
        )

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        accuracy = (tp + tn) / len(y_true) if len(y_true) > 0 else 0.0
        f1 = (
            2 * precision * recall / (precision + recall)
            if (precision + recall) > 0
            else 0.0
        )

        return {
            "precision": precision,
            "recall": recall,
            "accuracy": accuracy,
            "f1": f1,
            "tp": tp,
            "fp": fp,
            "tn": tn,
            "fn": fn,
        }

    @staticmethod
    def confusion_matrix(y_true: List[str], y_pred: List[str]) -> Dict[str, int]:
        """Generate confusion matrix. Returns: {tp, fp, tn, fn}."""
        tp = sum(
            1 for t, p in zip(y_true, y_pred) if t == "confounded" and p == "confounded"
        )
        fp = sum(
            1
            for t, p in zip(y_true, y_pred)
            if t == "unconfounded" and p == "confounded"
        )
        tn = sum(
            1
            for t, p in zip(y_true, y_pred)
            if t == "unconfounded" and p == "unconfounded"
        )
        fn = sum(
            1 for t, p in zip(y_true, y_pred) if t == "confounded" and p == "unconfounded"
        )

        return {"tp": tp, "fp": fp, "tn": tn, "fn": fn}
