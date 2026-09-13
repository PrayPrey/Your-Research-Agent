"""Conformal prediction with coverage guarantees."""

import numpy as np
from scipy.stats import rankdata


class ConformalPredictor:
    """Conformal prediction with coverage guarantees (aleatoric uncertainty)."""

    def __init__(
        self,
        coverage_target: float = 0.9,
        alpha: float = 0.1
    ):
        """Initialize conformal predictor."""
        self.coverage_target = coverage_target
        self.alpha = alpha
        self.calibration_scores = []
        self.quantile_threshold = 0.0

    def calibrate(
        self,
        calibration_data: list[tuple[float, bool]]
    ) -> None:
        """
        Calibrate conformal predictor on calibration set.

        Args:
            calibration_data: List of (conformity_score, is_correct) pairs
        """
        # Extract conformity scores
        self.calibration_scores = [score for score, _ in calibration_data]

        # Compute quantile threshold
        n = len(self.calibration_scores)
        q_level = np.ceil((n + 1) * (1 - self.alpha)) / n
        self.quantile_threshold = np.quantile(self.calibration_scores, q_level)

    def construct_interval(
        self,
        conformity_score: float
    ) -> int:
        """
        Construct prediction interval (membership indicator).

        Args:
            conformity_score: Conformity score for test sample

        Returns:
            int: 1 if in interval (I=1), 0 otherwise (I=0)
        """
        # Binary indicator: score <= threshold means in interval
        return 1 if conformity_score <= self.quantile_threshold else 0

    def compute_coverage(
        self,
        test_data: list[tuple[float, bool]]
    ) -> float:
        """
        Compute empirical coverage rate.

        Args:
            test_data: List of (conformity_score, is_correct) pairs

        Returns:
            float: Coverage rate (fraction of correct predictions in interval)
        """
        in_interval_count = 0
        correct_and_in_interval = 0

        for score, is_correct in test_data:
            in_interval = self.construct_interval(score)
            if in_interval:
                in_interval_count += 1
                if is_correct:
                    correct_and_in_interval += 1

        coverage = correct_and_in_interval / len(test_data) if test_data else 0.0
        return coverage
