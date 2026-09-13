"""Evaluation metrics for binary classification."""
from typing import List, Dict

class Evaluator:
    @staticmethod
    def compute_metrics(predictions: List[str], ground_truth: List[str]) -> Dict[str, float]:
        """Calculate FPR, precision, recall, accuracy. Returns metrics dict."""
        assert len(predictions) == len(ground_truth), "Length mismatch"

        tp = sum(1 for i in range(len(ground_truth))
                 if ground_truth[i] == "testable" and predictions[i] == "testable")
        fp = sum(1 for i in range(len(ground_truth))
                 if ground_truth[i] == "not_testable" and predictions[i] == "testable")
        tn = sum(1 for i in range(len(ground_truth))
                 if ground_truth[i] == "not_testable" and predictions[i] == "not_testable")
        fn = sum(1 for i in range(len(ground_truth))
                 if ground_truth[i] == "testable" and predictions[i] == "not_testable")

        # Primary metric: FPR = FP / (FP + TN)
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0

        # Secondary metrics
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        accuracy = (tp + tn) / len(ground_truth)
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

        # True Negative Rate (specificity)
        tnr = tn / (tn + fp) if (tn + fp) > 0 else 0.0

        return {
            "fpr": fpr,
            "precision": precision,
            "recall": recall,
            "accuracy": accuracy,
            "f1": f1,
            "tnr": tnr,
            "tp": tp,
            "fp": fp,
            "tn": tn,
            "fn": fn
        }

    @staticmethod
    def confusion_matrix(predictions: List[str], ground_truth: List[str]) -> Dict[str, int]:
        """Return confusion matrix as dict."""
        tp = sum(1 for i in range(len(ground_truth))
                 if ground_truth[i] == "testable" and predictions[i] == "testable")
        fp = sum(1 for i in range(len(ground_truth))
                 if ground_truth[i] == "not_testable" and predictions[i] == "testable")
        tn = sum(1 for i in range(len(ground_truth))
                 if ground_truth[i] == "not_testable" and predictions[i] == "not_testable")
        fn = sum(1 for i in range(len(ground_truth))
                 if ground_truth[i] == "testable" and predictions[i] == "not_testable")

        return {"tp": tp, "fp": fp, "tn": tn, "fn": fn}


if __name__ == "__main__":
    # Self-check
    preds = ["testable", "not_testable", "testable", "not_testable"]
    truth = ["testable", "not_testable", "not_testable", "testable"]

    metrics = Evaluator.compute_metrics(preds, truth)
    assert metrics["tp"] == 1, f"Expected TP=1, got {metrics['tp']}"
    assert metrics["fp"] == 1, f"Expected FP=1, got {metrics['fp']}"
    assert metrics["tn"] == 1, f"Expected TN=1, got {metrics['tn']}"
    assert metrics["fn"] == 1, f"Expected FN=1, got {metrics['fn']}"
    assert metrics["fpr"] == 0.5, f"Expected FPR=0.5, got {metrics['fpr']}"

    print("Evaluator self-check passed")
