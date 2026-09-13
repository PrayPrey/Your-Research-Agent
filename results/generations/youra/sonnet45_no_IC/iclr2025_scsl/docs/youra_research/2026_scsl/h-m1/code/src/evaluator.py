"""Evaluation Module for Repository Maintenance Classification."""

import numpy as np
import json
from typing import Tuple, Dict
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    classification_report,
    confusion_matrix
)


class GateEvaluator:
    """Evaluates model performance and checks gate conditions."""

    def __init__(self, accuracy_threshold: float = 0.75, f1_threshold: float = 0.73):
        """Initialize evaluator with gate thresholds.

        Args:
            accuracy_threshold: Minimum accuracy for MUST_WORK gate
            f1_threshold: Minimum F1 score for MUST_WORK gate
        """
        self.accuracy_threshold = accuracy_threshold
        self.f1_threshold = f1_threshold

    def compute_metrics(self, y_true: np.ndarray, y_pred: np.ndarray, y_proba: np.ndarray = None) -> Dict:
        """Compute all evaluation metrics.

        Args:
            y_true: Ground truth labels
            y_pred: Predicted labels
            y_proba: Predicted probabilities (optional, for ROC-AUC)

        Returns:
            Dict with all computed metrics
        """
        metrics = {
            'accuracy': float(accuracy_score(y_true, y_pred)),
            'precision': float(precision_score(y_true, y_pred, zero_division=0)),
            'recall': float(recall_score(y_true, y_pred, zero_division=0)),
            'f1': float(f1_score(y_true, y_pred, zero_division=0))
        }

        # ROC-AUC (requires probabilities)
        if y_proba is not None:
            try:
                if y_proba.ndim > 1:
                    # Use probability of positive class (class 1)
                    y_proba_positive = y_proba[:, 1]
                else:
                    y_proba_positive = y_proba
                metrics['roc_auc'] = float(roc_auc_score(y_true, y_proba_positive))
            except Exception as e:
                print(f"Warning: Could not compute ROC-AUC: {e}")
                metrics['roc_auc'] = None

        # Confusion matrix
        cm = confusion_matrix(y_true, y_pred)
        metrics['confusion_matrix'] = {
            'tn': int(cm[0, 0]),
            'fp': int(cm[0, 1]),
            'fn': int(cm[1, 0]),
            'tp': int(cm[1, 1])
        }

        # Class-specific metrics
        metrics['class_distribution'] = {
            'true_negatives': int((y_true == 0).sum()),
            'true_positives': int((y_true == 1).sum()),
            'pred_negatives': int((y_pred == 0).sum()),
            'pred_positives': int((y_pred == 1).sum())
        }

        return metrics

    def check_gate_status(self, metrics: Dict) -> Tuple[bool, str]:
        """Evaluate gate condition based on computed metrics.

        Args:
            metrics: Dict with accuracy and f1 scores

        Returns:
            Tuple of (gate_passed, explanation)
        """
        accuracy = metrics['accuracy']
        f1 = metrics['f1']

        accuracy_passed = accuracy >= self.accuracy_threshold
        f1_passed = f1 >= self.f1_threshold

        if accuracy_passed and f1_passed:
            explanation = (
                f"PASS - Both criteria met:\n"
                f"  Accuracy: {accuracy:.4f} ≥ {self.accuracy_threshold:.2f} ✓\n"
                f"  F1 Score: {f1:.4f} ≥ {self.f1_threshold:.2f} ✓"
            )
            return True, explanation
        else:
            reasons = []
            if not accuracy_passed:
                reasons.append(f"Accuracy: {accuracy:.4f} < {self.accuracy_threshold:.2f} ✗")
            if not f1_passed:
                reasons.append(f"F1 Score: {f1:.4f} < {self.f1_threshold:.2f} ✗")

            explanation = "FAIL - Gate criteria not met:\n  " + "\n  ".join(reasons)
            return False, explanation

    def generate_classification_report(self, y_true: np.ndarray, y_pred: np.ndarray) -> str:
        """Generate sklearn classification report with per-class metrics.

        Args:
            y_true: Ground truth labels
            y_pred: Predicted labels

        Returns:
            Classification report string
        """
        report = classification_report(
            y_true,
            y_pred,
            target_names=['Abandoned', 'Maintained'],
            zero_division=0
        )
        return report

    def generate_classification_report_dict(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict:
        """Generate sklearn classification report as dictionary.

        Args:
            y_true: Ground truth labels
            y_pred: Predicted labels

        Returns:
            Classification report as dict
        """
        report = classification_report(
            y_true,
            y_pred,
            target_names=['Abandoned', 'Maintained'],
            output_dict=True,
            zero_division=0
        )
        return report

    def save_metrics(self, metrics: Dict, report_path: str) -> None:
        """Save metrics to JSON file.

        Args:
            metrics: Dict with computed metrics
            report_path: Path to save JSON file
        """
        # Convert numpy types to native Python types
        def convert_types(obj):
            if isinstance(obj, dict):
                return {k: convert_types(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_types(item) for item in obj]
            elif isinstance(obj, (np.integer, np.floating)):
                return float(obj)
            elif isinstance(obj, (np.ndarray,)):
                return obj.tolist()
            elif isinstance(obj, (np.bool_,)):
                return bool(obj)
            return obj

        metrics_clean = convert_types(metrics)

        with open(report_path, 'w') as f:
            json.dump(metrics_clean, f, indent=2)

        print(f"Metrics saved to {report_path}")

    def print_summary(self, metrics: Dict, gate_passed: bool, gate_explanation: str) -> None:
        """Print evaluation summary to console.

        Args:
            metrics: Dict with computed metrics
            gate_passed: Whether gate condition was met
            gate_explanation: Explanation of gate result
        """
        print("\n" + "=" * 60)
        print("EVALUATION RESULTS")
        print("=" * 60)
        print(f"\nMetrics:")
        print(f"  Accuracy:  {metrics['accuracy']:.4f}")
        print(f"  Precision: {metrics['precision']:.4f}")
        print(f"  Recall:    {metrics['recall']:.4f}")
        print(f"  F1 Score:  {metrics['f1']:.4f}")
        if metrics.get('roc_auc'):
            print(f"  ROC-AUC:   {metrics['roc_auc']:.4f}")

        print(f"\nConfusion Matrix:")
        cm = metrics['confusion_matrix']
        print(f"  TN: {cm['tn']:4d}  FP: {cm['fp']:4d}")
        print(f"  FN: {cm['fn']:4d}  TP: {cm['tp']:4d}")

        print(f"\n{gate_explanation}")
        print("=" * 60)
