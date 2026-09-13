"""Model implementations for h-m2 Shape Descriptor experiment.

Implements ShapeDescriptorAnalyzer (proposed) and BaselineDescriptor (baseline)
for computing shape descriptors on cluster centroids.
"""

import numpy as np
from typing import Dict, List, Tuple
from scipy.signal import find_peaks
import ruptures as rpt

from config import ExperimentConfig


class ShapeDescriptorAnalyzer:
    """
    Compute shape descriptors for time series centroids.
    Tests if clusters have distinct shape signatures.

    Descriptors:
    1. growth_ratio: fraction of positive gradient values
    2. peak_timing: normalized position of first peak
    3. changepoint_count: number of PELT changepoints
    4. derivative_variance: variance of gradient
    """

    def __init__(self, config: ExperimentConfig) -> None:
        self.config = config
        self.min_prominence = config.min_prominence
        self.pelt_model = config.pelt_model
        self.pelt_min_size = config.pelt_min_size

    def compute_descriptors(self, centroid: np.ndarray) -> Dict[str, float]:
        """
        Compute 4 shape descriptors for a single centroid.

        Args:
            centroid: (T,) normalized time series

        Returns:
            dict with keys: growth_ratio, peak_timing, changepoint_count, derivative_variance
        """
        # Handle NaN values (from padding)
        centroid = np.nan_to_num(centroid, nan=0.0)

        # Find actual length (non-zero portion)
        nonzero_mask = centroid != 0
        if not nonzero_mask.any():
            # All zeros - return default values
            return {
                "growth_ratio": 0.5,
                "peak_timing": 0.5,
                "changepoint_count": 0,
                "derivative_variance": 0.0
            }

        # Use full centroid for analysis
        T = len(centroid)

        # 1. Derivative sign pattern (growth vs decline phases)
        gradient = np.gradient(centroid)
        sign_pattern = np.sign(gradient)
        growth_ratio = float(np.mean(sign_pattern > 0))

        # 2. Peak timing (when does trajectory peak?)
        try:
            # Use adaptive prominence based on data range
            data_range = np.max(centroid) - np.min(centroid)
            prominence = max(self.min_prominence * data_range, 0.01)
            peaks, _ = find_peaks(centroid, prominence=prominence)
            if len(peaks) > 0:
                peak_timing = float(peaks[0] / T)
            else:
                # No peaks found - use argmax as fallback
                peak_timing = float(np.argmax(centroid) / T)
        except Exception:
            peak_timing = 0.5

        # 3. Changepoint count (from h-m1 methodology)
        try:
            # Ensure minimum length for PELT
            if T >= self.pelt_min_size * 2:
                algo = rpt.Pelt(model=self.pelt_model, min_size=self.pelt_min_size).fit(centroid)
                pen = 2 * np.log(T)
                changepoints = algo.predict(pen=pen)
                n_changepoints = len(changepoints) - 1  # Exclude endpoint
            else:
                n_changepoints = 0
        except Exception:
            n_changepoints = 0

        # 4. Derivative variance
        derivative_variance = float(np.var(gradient))

        return {
            "growth_ratio": growth_ratio,
            "peak_timing": peak_timing,
            "changepoint_count": n_changepoints,
            "derivative_variance": derivative_variance
        }

    def compute_descriptor_matrix(
        self, centroids: np.ndarray
    ) -> Tuple[np.ndarray, List[str]]:
        """
        Apply compute_descriptors to all k centroids.

        Args:
            centroids: (k, T)

        Returns:
            (descriptor_matrix, descriptor_names)
            descriptor_matrix: (k, 4) float array
            descriptor_names: List[str] length 4
        """
        descriptor_names = ["growth_ratio", "peak_timing", "changepoint_count", "derivative_variance"]

        k = centroids.shape[0]
        descriptor_matrix = np.zeros((k, 4), dtype=np.float64)

        for i in range(k):
            desc = self.compute_descriptors(centroids[i])
            for j, name in enumerate(descriptor_names):
                descriptor_matrix[i, j] = desc[name]

        return descriptor_matrix, descriptor_names

    def normalize_descriptors(self, descriptor_matrix: np.ndarray) -> np.ndarray:
        """
        Min-max normalize each descriptor column to [0, 1].

        Args:
            descriptor_matrix: (k, 4)

        Returns:
            normalized: (k, 4)
        """
        normalized = np.zeros_like(descriptor_matrix)

        for j in range(descriptor_matrix.shape[1]):
            col = descriptor_matrix[:, j]
            col_min, col_max = col.min(), col.max()
            if col_max - col_min > 1e-10:
                normalized[:, j] = (col - col_min) / (col_max - col_min)
            else:
                normalized[:, j] = 0.5  # All values same

        return normalized


class BaselineDescriptor:
    """
    Baseline descriptor using simple summary statistics only.

    Descriptors: mean, std, trend (linear slope)
    """

    def __init__(self, config: ExperimentConfig) -> None:
        self.config = config

    def compute_descriptors(self, centroid: np.ndarray) -> Dict[str, float]:
        """
        Baseline: simple summary statistics only.

        Args:
            centroid: (T,) time series

        Returns:
            dict with keys: mean, std, trend
        """
        # Handle NaN values
        centroid = np.nan_to_num(centroid, nan=0.0)

        mean_val = float(np.mean(centroid))
        std_val = float(np.std(centroid))

        # Trend via linear regression
        t = np.arange(len(centroid))
        if len(centroid) > 1:
            trend = float(np.polyfit(t, centroid, 1)[0])
        else:
            trend = 0.0

        return {
            "mean": mean_val,
            "std": std_val,
            "trend": trend
        }

    def compute_descriptor_matrix(
        self, centroids: np.ndarray
    ) -> Tuple[np.ndarray, List[str]]:
        """
        Args:
            centroids: (k, T)

        Returns:
            (descriptor_matrix, descriptor_names)
            descriptor_matrix: (k, 3)
        """
        descriptor_names = ["mean", "std", "trend"]

        k = centroids.shape[0]
        descriptor_matrix = np.zeros((k, 3), dtype=np.float64)

        for i in range(k):
            desc = self.compute_descriptors(centroids[i])
            for j, name in enumerate(descriptor_names):
                descriptor_matrix[i, j] = desc[name]

        return descriptor_matrix, descriptor_names
