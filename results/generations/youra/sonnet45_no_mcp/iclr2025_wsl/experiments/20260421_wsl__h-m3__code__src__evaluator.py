"""Evaluator: Compute metrics and check gate conditions
Extended from h-e1 with h-m1-specific validation
"""

import numpy as np
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score


class Evaluator:
    """Compute metrics and check gate conditions."""

    def compute_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> dict:
        """Compute classification metrics.

        Args:
            y_true: True labels [N,]
            y_pred: Predicted labels [N,]

        Returns:
            Dictionary with confusion_matrix and classification_report
        """
        cm = confusion_matrix(y_true, y_pred)
        report = classification_report(
            y_true, y_pred,
            target_names=['shallow', 'deep'],
            output_dict=True
        )

        return {
            'confusion_matrix': cm,
            'classification_report': report,
            'accuracy': accuracy_score(y_true, y_pred)
        }

    def verify_mechanism(self, results: dict) -> list:
        """Verify gradient-flow mechanism indicators.

        Args:
            results: Dictionary with experiment results

        Returns:
            List of boolean indicators:
                [0] Features Extracted (6 gradient-flow features)
                [1] Layer Positions Valid (normalized [0, 1])
                [2] Classifier Trained (accuracy > 0)
                [3] Gradient Effect Detected (test accuracy > random)
        """
        indicators = []

        # [0] Features Extracted: Should have 6 features per model
        features_extracted = (results.get('feature_shape') == (6,))
        indicators.append(features_extracted)

        # [1] Layer Positions Valid: Check layer count range
        min_layers = results.get('min_layer_count', 0)
        max_layers = results.get('max_layer_count', 0)
        layer_positions_valid = (min_layers > 0 and max_layers > min_layers)
        indicators.append(layer_positions_valid)

        # [2] Classifier Trained: Train accuracy should be > 0
        train_accuracy = results.get('train_accuracy', 0)
        classifier_trained = (train_accuracy > 0)
        indicators.append(classifier_trained)

        # [3] Gradient Effect Detected: Test accuracy > random baseline (0.5)
        test_accuracy = results.get('test_accuracy', 0)
        effect_detected = (test_accuracy > 0.5)
        indicators.append(effect_detected)

        return indicators

    def check_gate_condition(self, test_accuracy: float, threshold: float = 0.5) -> bool:
        """Check if gate condition is satisfied.

        Args:
            test_accuracy: Test set accuracy
            threshold: Minimum threshold (default: 0.5 for h-m1 MUST_WORK gate)

        Returns:
            True if gate passed, False otherwise
        """
        return test_accuracy > threshold

    def compare_with_baseline(self, h_m1_accuracy: float, h_e1_accuracy: float,
                              random_accuracy: float = None) -> dict:
        """Compare h-m1 performance with h-e1 baseline and random test.

        Args:
            h_m1_accuracy: H-M1 test accuracy (gradient-flow features)
            h_e1_accuracy: H-E1 test accuracy (all weight statistics)
            random_accuracy: Random model test accuracy (optional)

        Returns:
            Dictionary with comparison metrics and interpretation
        """
        performance_gap = h_e1_accuracy - h_m1_accuracy

        # Interpret mechanism contribution
        if h_m1_accuracy >= h_e1_accuracy:
            interpretation = "Gradient flow is sufficient mechanism"
            contribution = "FULL"
        elif h_m1_accuracy >= 0.70:
            interpretation = "Gradient flow is strong contributor"
            contribution = "STRONG"
        elif h_m1_accuracy >= 0.50:
            interpretation = "Gradient flow is partial contributor"
            contribution = "PARTIAL"
        else:
            interpretation = "Gradient flow not a mechanism (FAIL)"
            contribution = "NONE"

        comparison = {
            'h_e1_accuracy': h_e1_accuracy,
            'h_m1_accuracy': h_m1_accuracy,
            'performance_gap': performance_gap,
            'interpretation': interpretation,
            'contribution': contribution
        }

        # Add random test validation if available
        if random_accuracy is not None:
            comparison['random_accuracy'] = random_accuracy
            comparison['random_vs_pretrained_gap'] = h_m1_accuracy - random_accuracy
            comparison['training_induced'] = (random_accuracy < 0.55)

        return comparison
