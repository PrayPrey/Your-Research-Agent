"""Statistical analysis module.

This module computes distributional statistics and evaluates gate conditions.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any


class StatisticalAnalyzer:
    """Analyzer for distributional statistics and gate evaluation."""

    def __init__(self, random_seed: int = 42):
        """Initialize analyzer.

        Args:
            random_seed: Random seed for reproducibility
        """
        self.random_seed = random_seed
        np.random.seed(random_seed)

    def compute_statistics(self, features: np.ndarray) -> Dict[str, float]:
        """Compute distributional statistics.

        Args:
            features: Array of feature values

        Returns:
            Dictionary with mean, std, cv, min, max, median
        """
        if len(features) == 0:
            return {
                'mean': 0.0,
                'std': 0.0,
                'cv': 0.0,
                'min': 0.0,
                'max': 0.0,
                'median': 0.0
            }

        mean = np.mean(features)
        std = np.std(features)
        cv = std / mean if mean > 0 else 0.0

        return {
            'mean': float(mean),
            'std': float(std),
            'cv': float(cv),
            'min': float(np.min(features)),
            'max': float(np.max(features)),
            'median': float(np.median(features))
        }

    def compute_cv(self, features: np.ndarray) -> float:
        """Compute coefficient of variation.

        Args:
            features: Array of feature values

        Returns:
            Coefficient of variation (std / mean)
        """
        if len(features) == 0:
            return 0.0

        mean = np.mean(features)
        std = np.std(features)

        return std / mean if mean > 0 else 0.0

    def cross_split_validation(self, split_features: Dict[str, np.ndarray]) -> Dict[str, Dict[str, float]]:
        """Compute statistics per split.

        Args:
            split_features: Dictionary mapping split names to feature arrays

        Returns:
            Dictionary mapping split names to their statistics
        """
        split_stats = {}

        for split_name, features in split_features.items():
            split_stats[split_name] = self.compute_statistics(features)

        return split_stats

    def gate_evaluation(self, cv: float, precision: float,
                       cv_threshold: float = 0.3,
                       precision_threshold: float = 0.9) -> bool:
        """Evaluate gate condition.

        Args:
            cv: Coefficient of variation
            precision: Extraction precision
            cv_threshold: Minimum required CV
            precision_threshold: Minimum required precision

        Returns:
            True if gate passes, False otherwise
        """
        return (cv > cv_threshold) and (precision > precision_threshold)

    def estimate_precision(self, features: np.ndarray, sample_size: int = 100) -> float:
        """Estimate extraction precision via sampling.

        For PoC purposes, we use a proxy: check if features are non-zero
        and have reasonable variance. In production, this would involve
        manual validation of a sample.

        Args:
            features: Array of feature values
            sample_size: Number of samples to check

        Returns:
            Estimated precision (0.0 to 1.0)
        """
        if len(features) == 0:
            return 0.0

        # Sample random indices
        sample_indices = np.random.choice(
            len(features),
            size=min(sample_size, len(features)),
            replace=False
        )
        sample_features = features[sample_indices]

        # Proxy for precision: percentage of non-zero, reasonable values
        non_zero = np.sum(sample_features > 0)
        reasonable = np.sum((sample_features >= 0) & (sample_features <= 100))

        precision = reasonable / len(sample_features)

        return float(precision)
