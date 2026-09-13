"""Ablation Framework for h-m3.

Evaluates 7 detector variants (single-signal, pairwise, hybrid).
"""

import sys
from pathlib import Path
from typing import Dict, List, Callable, Any
import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score
from scipy.stats import pearsonr, spearmanr

# Add detectors directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "detectors"))

from hybrid_detector import HybridTerminationDetector


class AblationFramework:
    """Framework for evaluating 7 detector variants."""

    def __init__(self, thresholds: Dict[str, float]):
        """Initialize framework.

        Args:
            thresholds: Threshold dictionary for all signals
        """
        self.thresholds = thresholds
        self.models = self._create_models()

    def _create_models(self) -> Dict[str, Callable]:
        """Create 7 detector variants.

        Returns:
            Dictionary mapping model names to detector functions
        """
        t = self.thresholds

        models = {
            # Single-signal models
            'confidence_only': lambda s: s['confidence_variance'] > t['confidence_variance'],
            'symbolic_only': lambda s: (s['state_collisions'] > t['state_collisions'] or
                                       s['exponential_growth'] > t['exponential_growth']),
            'search_only': lambda s: s['backtrack_freq'] > t['backtrack_freq'],

            # Pairwise combinations (OR logic)
            'conf_symb': lambda s: (s['confidence_variance'] > t['confidence_variance'] or
                                   s['state_collisions'] > t['state_collisions'] or
                                   s['exponential_growth'] > t['exponential_growth']),
            'conf_search': lambda s: (s['confidence_variance'] > t['confidence_variance'] or
                                     s['backtrack_freq'] > t['backtrack_freq']),
            'symb_search': lambda s: (s['state_collisions'] > t['state_collisions'] or
                                     s['exponential_growth'] > t['exponential_growth'] or
                                     s['backtrack_freq'] > t['backtrack_freq']),

            # Hybrid (k=2 voting)
            'hybrid_all': self._hybrid_detector
        }

        return models

    def _hybrid_detector(self, signals: Dict[str, float]) -> bool:
        """Hybrid detector with k=2 voting.

        Args:
            signals: Signal dictionary

        Returns:
            True if at least 2 of 3 signal groups trigger
        """
        t = self.thresholds

        # Three signal groups
        conf_alert = signals['confidence_variance'] > t['confidence_variance']
        symb_alert = (signals['state_collisions'] > t['state_collisions'] or
                     signals['exponential_growth'] > t['exponential_growth'])
        search_alert = signals['backtrack_freq'] > t['backtrack_freq']

        # k=2 voting
        votes = sum([conf_alert, symb_alert, search_alert])
        return votes >= 2

    def evaluate_all_models(self, signals_list: List[Dict[str, float]],
                           ground_truth: List[int]) -> Dict[str, Dict[str, float]]:
        """Evaluate all models on dataset.

        Args:
            signals_list: List of signal dictionaries (one per theorem)
            ground_truth: List of labels (0=success, 1=timeout)

        Returns:
            Dictionary mapping model names to metrics dictionaries:
                - precision, recall, f1, pearson_r, spearman_rho
        """
        results = {}

        for model_name, model_func in self.models.items():
            # Generate predictions
            predictions = [int(model_func(s)) for s in signals_list]

            # Calculate metrics
            precision = precision_score(ground_truth, predictions, zero_division=0)
            recall = recall_score(ground_truth, predictions, zero_division=0)
            f1 = f1_score(ground_truth, predictions, zero_division=0)

            # Correlation metrics
            try:
                pearson_r, pearson_p = pearsonr(ground_truth, predictions)
            except:
                pearson_r, pearson_p = 0.0, 1.0

            try:
                spearman_rho, spearman_p = spearmanr(ground_truth, predictions)
            except:
                spearman_rho, spearman_p = 0.0, 1.0

            results[model_name] = {
                'precision': float(precision),
                'recall': float(recall),
                'f1': float(f1),
                'pearson_r': float(pearson_r),
                'pearson_p': float(pearson_p),
                'spearman_rho': float(spearman_rho),
                'spearman_p': float(spearman_p)
            }

        return results

    def check_gate_condition(self, results: Dict[str, Dict[str, float]]) -> bool:
        """Check if hybrid outperforms all single-signal ablations.

        Gate condition: hybrid_all F1 > max(single-signal F1s)

        Args:
            results: Results from evaluate_all_models()

        Returns:
            True if gate condition satisfied
        """
        # Get F1 scores
        hybrid_f1 = results['hybrid_all']['f1']

        single_signal_models = ['confidence_only', 'symbolic_only', 'search_only']
        single_f1s = [results[m]['f1'] for m in single_signal_models]

        max_single_f1 = max(single_f1s) if single_f1s else 0.0

        # Check gate
        return hybrid_f1 > max_single_f1
