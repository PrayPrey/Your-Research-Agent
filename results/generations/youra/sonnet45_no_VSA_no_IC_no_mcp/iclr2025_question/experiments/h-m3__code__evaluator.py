"""Evaluation module for viability classification."""

from sklearn.metrics import accuracy_score, confusion_matrix
from scipy.stats import binom_test


class ClassificationEvaluator:
    """Compute accuracy, confusion matrix, and binomial test."""

    def compute_accuracy(self, y_true: list, y_pred: list) -> float:
        """Compute classification accuracy: (TP + TN) / Total."""
        return accuracy_score(y_true, y_pred)

    def compute_confusion_matrix(self, y_true: list, y_pred: list) -> dict:
        """
        Compute confusion matrix (TP/TN/FP/FN).

        Returns:
            dict with keys: TP, TN, FP, FN
        """
        cm = confusion_matrix(y_true, y_pred, labels=["viable", "non-viable"])
        TN, FP, FN, TP = cm.ravel()
        return {"TP": int(TP), "TN": int(TN), "FP": int(FP), "FN": int(FN)}

    def binomial_test(self, n_correct: int, n_total: int, null_p: float = 0.5) -> tuple[float, bool]:
        """
        Test if accuracy significantly exceeds null hypothesis (random guessing).

        Args:
            n_correct: Number of correct predictions
            n_total: Total number of predictions
            null_p: Null hypothesis probability (default 0.5)

        Returns:
            (p_value, significant) where significant = p_value < 0.05
        """
        p_value = binom_test(n_correct, n_total, p=null_p, alternative='greater')
        return float(p_value), bool(p_value < 0.05)

    def generate_metrics_dict(self, y_true: list, y_pred_baseline: list, y_pred_gate1: list) -> dict:
        """Generate full metrics dict for both baseline and Gate 1."""
        acc_baseline = self.compute_accuracy(y_true, y_pred_baseline)
        acc_gate1 = self.compute_accuracy(y_true, y_pred_gate1)

        cm_baseline = self.compute_confusion_matrix(y_true, y_pred_baseline)
        cm_gate1 = self.compute_confusion_matrix(y_true, y_pred_gate1)

        n_correct_baseline = int(acc_baseline * len(y_true))
        n_correct_gate1 = int(acc_gate1 * len(y_true))

        p_baseline, sig_baseline = self.binomial_test(n_correct_baseline, len(y_true))
        p_gate1, sig_gate1 = self.binomial_test(n_correct_gate1, len(y_true))

        return {
            "baseline": {
                "accuracy": acc_baseline,
                "n_correct": n_correct_baseline,
                "n_total": len(y_true),
                "p_value": p_baseline,
                "significant": sig_baseline,
                "confusion_matrix": cm_baseline
            },
            "gate1": {
                "accuracy": acc_gate1,
                "n_correct": n_correct_gate1,
                "n_total": len(y_true),
                "p_value": p_gate1,
                "significant": sig_gate1,
                "confusion_matrix": cm_gate1
            }
        }
