"""Evaluator: Compute metrics and verify gate condition"""

import numpy as np
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from typing import Dict, Tuple


class Evaluator:
    """Compute metrics and verify gate condition."""

    def compute_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict:
        """Compute accuracy, confusion matrix, classification report."""
        metrics = {
            'accuracy': accuracy_score(y_true, y_pred),
            'confusion_matrix': confusion_matrix(y_true, y_pred),
            'classification_report': classification_report(
                y_true, y_pred,
                target_names=['shallow', 'deep'],
                output_dict=True
            )
        }
        return metrics

    def verify_mechanism(self, results: Dict) -> Tuple[bool, bool, bool, bool]:
        """Check 4 activation indicators. Returns: (feat_ext, norms_valid, trained, effect)"""
        features_extracted = (
            results.get('num_models') == 20 and
            results.get('feature_shape') == (4,)
        )

        layer_norms_valid = (
            results.get('min_layer_count', 0) > 0 and
            results.get('max_layer_count', 0) > 0
        )

        classifier_trained = (
            results.get('train_accuracy') is not None and
            results.get('train_accuracy') > 0
        )

        effect_detected = results.get('test_accuracy', 0) > 0.50

        return (features_extracted, layer_norms_valid, classifier_trained, effect_detected)

    def check_gate_condition(self, test_accuracy: float, threshold: float = 0.70) -> bool:
        """Gate check: test_accuracy >= threshold. Returns: PASS/FAIL"""
        gate_passed = test_accuracy >= threshold

        status = "PASS" if gate_passed else "FAIL"
        print(f"\n{'='*60}")
        print(f"GATE CONDITION CHECK")
        print(f"{'='*60}")
        print(f"Test Accuracy: {test_accuracy:.2%}")
        print(f"Threshold:     {threshold:.2%}")
        print(f"Gate Status:   {status}")
        print(f"{'='*60}")

        return gate_passed
