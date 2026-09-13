"""
NMI Evaluator for h-m-integrated
Normalized Mutual Information computation and baseline comparison
"""

import numpy as np
from sklearn.metrics import normalized_mutual_info_score
from typing import Dict


class NMIEvaluator:
    """NMI computation and baseline comparison."""

    def __init__(self, config):
        """
        Initialize NMI evaluator.

        Args:
            config: ExperimentConfig instance
        """
        self.config = config
        self.nmi_config = config.nmi

    def compute_nmi(self, labels_true: np.ndarray, labels_pred: np.ndarray) -> float:
        """
        Compute Normalized Mutual Information.

        Args:
            labels_true: [N] true labels
            labels_pred: [N] predicted labels

        Returns:
            float: NMI score [0, 1]
        """
        nmi = normalized_mutual_info_score(
            labels_true,
            labels_pred,
            average_method=self.nmi_config.average_method
        )
        return float(nmi)

    def compute_all_nmi(self, labels_true: np.ndarray, predictions: Dict[str, np.ndarray]) -> Dict[str, float]:
        """
        Compute NMI for all methods.

        Args:
            labels_true: [N] true labels
            predictions: Dict mapping method name to predicted labels

        Returns:
            Dict[str, float]: NMI scores for each method
        """
        nmi_scores = {}
        for method_name, labels_pred in predictions.items():
            nmi = self.compute_nmi(labels_true, labels_pred)
            nmi_scores[method_name] = nmi
            print(f"NMI({method_name}): {nmi:.4f}")

        return nmi_scores

    def compute_baseline_gap(self, nmi_scores: Dict[str, float]) -> float:
        """
        Compute gap between semantic and best baseline.

        Args:
            nmi_scores: Dict of NMI scores for all methods

        Returns:
            float: Baseline gap (semantic - max(baselines))
        """
        semantic_nmi = nmi_scores.get('semantic', 0.0)

        baseline_methods = ['permutation', 'lda', 'lexical']
        baseline_nmis = [nmi_scores.get(m, 0.0) for m in baseline_methods if m in nmi_scores]

        if not baseline_nmis:
            print("Warning: No baseline NMI scores found")
            return 0.0

        max_baseline = max(baseline_nmis)
        gap = semantic_nmi - max_baseline

        print(f"Semantic NMI: {semantic_nmi:.4f}")
        print(f"Best baseline NMI: {max_baseline:.4f} ({baseline_methods[baseline_nmis.index(max_baseline)]})")
        print(f"Baseline gap: {gap:.4f}")

        return float(gap)

    def evaluate_controls(
        self,
        labels_true: np.ndarray,
        original_predictions: np.ndarray,
        normalized_predictions: np.ndarray,
        filtered_predictions: np.ndarray
    ) -> Dict[str, float]:
        """
        Evaluate control experiments.

        Args:
            labels_true: True labels
            original_predictions: Original clustering predictions
            normalized_predictions: Length-normalized clustering predictions
            filtered_predictions: Modality-filtered clustering predictions

        Returns:
            Dict[str, float]: Control experiment NMI scores
        """
        control_results = {
            'original': self.compute_nmi(labels_true, original_predictions),
            'length_normalized': self.compute_nmi(labels_true, normalized_predictions),
            'modality_filtered': self.compute_nmi(labels_true, filtered_predictions)
        }

        print("\nControl Experiment Results:")
        for control_name, nmi in control_results.items():
            print(f"  {control_name}: {nmi:.4f}")

        return control_results
