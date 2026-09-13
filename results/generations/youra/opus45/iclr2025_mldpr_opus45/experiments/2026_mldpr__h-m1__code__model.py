"""Model implementations for h-m1 PELT changepoint detection experiment.

Contains:
- BaselineDetector: Null baselines (random, none, fixed-interval)
- PELTDetector: PELT changepoint detection with BIC penalty
"""

import numpy as np
import ruptures as rpt
from typing import List, Tuple, Dict

from config import ExperimentConfig


class BaselineDetector:
    """Null baselines for changepoint detection comparison."""

    def __init__(self, config: ExperimentConfig) -> None:
        self.config = config
        self.rng = np.random.RandomState(config.random_state)

    def detect_random(self, series: np.ndarray) -> List[int]:
        """
        Place 0-4 changepoints uniformly at random.

        Args:
            series: (T,) 1D time series

        Returns:
            List of changepoint indices (excluding endpoint)
        """
        T = len(series)
        min_size = self.config.pelt_min_size

        # Random number of changepoints (0-4)
        n_cps = self.rng.randint(0, 5)

        if n_cps == 0 or T < 2 * min_size:
            return []

        # Valid positions (exclude first min_size and last min_size)
        valid_range = range(min_size, T - min_size)
        if len(valid_range) < n_cps:
            n_cps = len(valid_range)

        if n_cps == 0:
            return []

        changepoints = sorted(self.rng.choice(list(valid_range), size=n_cps, replace=False))
        return list(changepoints)

    def detect_none(self, series: np.ndarray) -> List[int]:
        """
        Null model: assume no changepoints exist.

        Args:
            series: (T,) 1D time series

        Returns:
            Empty list
        """
        return []

    def detect_fixed_interval(self, series: np.ndarray, interval: int = 6) -> List[int]:
        """
        Place changepoints at fixed intervals.

        Args:
            series: (T,) 1D time series
            interval: Gap between changepoints

        Returns:
            List of changepoint indices
        """
        T = len(series)
        min_size = self.config.pelt_min_size

        changepoints = []
        pos = interval
        while pos < T - min_size:
            changepoints.append(pos)
            pos += interval

        return changepoints

    def compute_detection_rate(
        self, all_series: List[np.ndarray], method: str = "random"
    ) -> float:
        """
        Compute proportion of series with at least one changepoint.

        Args:
            all_series: List of 1D time series
            method: "random", "none", or "fixed_interval"

        Returns:
            Detection rate in [0, 1]
        """
        if method == "random":
            detect_fn = self.detect_random
        elif method == "none":
            detect_fn = self.detect_none
        elif method == "fixed_interval":
            detect_fn = self.detect_fixed_interval
        else:
            raise ValueError(f"Unknown method: {method}")

        n_with_cp = sum(1 for ts in all_series if len(detect_fn(ts)) > 0)
        return n_with_cp / len(all_series) if all_series else 0.0


class PELTDetector:
    """PELT changepoint detection with BIC penalty."""

    def __init__(self, config: ExperimentConfig) -> None:
        self.config = config
        self.model = config.pelt_model
        self.min_size = config.pelt_min_size
        self.jump = config.pelt_jump
        self.penalty_range = config.penalty_range
        self.n_penalties = config.n_penalties

    def detect(self, series: np.ndarray) -> Tuple[List[int], float]:
        """
        Run PELT with BIC penalty on single series.

        Args:
            series: (T,) 1D time series (preprocessed)

        Returns:
            (changepoints, optimal_penalty) where changepoints excludes endpoint
        """
        # Ensure 1D array
        series = np.asarray(series).flatten()
        n = len(series)

        if n < 2 * self.min_size:
            return [], 0.0

        # Fit PELT algorithm
        algo = rpt.Pelt(model=self.model, min_size=self.min_size, jump=self.jump)
        algo.fit(series)

        # BIC penalty: pen = 2 * log(n)
        pen = 2 * np.log(n)

        # Predict changepoints
        result = algo.predict(pen=pen)

        # Exclude endpoint (ruptures includes T as last element)
        changepoints = result[:-1] if result else []

        return changepoints, pen

    def detect_all(
        self, all_series: List[np.ndarray]
    ) -> Tuple[List[List[int]], float]:
        """
        Apply PELT to all series.

        Args:
            all_series: List of 1D time series (preprocessed)

        Returns:
            (all_changepoints, detection_rate)
        """
        all_changepoints = []
        n_with_cp = 0

        for ts in all_series:
            cps, _ = self.detect(ts)
            all_changepoints.append(cps)
            if len(cps) > 0:
                n_with_cp += 1

        detection_rate = n_with_cp / len(all_series) if all_series else 0.0

        return all_changepoints, detection_rate

    def penalty_sensitivity(
        self, series: np.ndarray
    ) -> List[Tuple[float, int, List[int]]]:
        """
        CROPS-style grid search over penalty range.

        Args:
            series: (T,) 1D time series

        Returns:
            List of (penalty, n_changepoints, changepoints) sorted by penalty
        """
        series = np.asarray(series).flatten()
        n = len(series)

        if n < 2 * self.min_size:
            return []

        # Fit PELT algorithm
        algo = rpt.Pelt(model=self.model, min_size=self.min_size, jump=self.jump)
        algo.fit(series)

        # Log-spaced penalties
        penalties = np.logspace(
            np.log10(self.penalty_range[0]),
            np.log10(self.penalty_range[1]),
            self.n_penalties
        )

        results = []
        for pen in penalties:
            bkps = algo.predict(pen=pen)
            cps = bkps[:-1] if bkps else []  # Exclude endpoint
            n_cps = len(cps)
            results.append((float(pen), n_cps, cps))

        return results
