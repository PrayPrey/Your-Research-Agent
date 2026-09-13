"""Curvature timing analysis module for H-M1 experiment.

Implements CurvatureTimingAnalyzer for computing second derivatives of
loss trajectories and detecting sign-flip epochs (curvature stabilization).

Core hypothesis: Minority samples show delayed curvature stabilization
(sign-flip epoch >= 3 epochs later than majority in >= 70% of seeds).
"""

from typing import Any, Dict

import numpy as np
from scipy.ndimage import gaussian_filter1d


class CurvatureTimingAnalyzer:
    """Analyze curvature timing of per-sample loss trajectories.

    Computes second derivatives (curvature) of normalized loss curves and
    detects sign-flip epochs where curvature transitions from convex
    (negative) to stable (near-zero).

    H-M1 Hypothesis: Minority samples show delayed curvature stabilization
    (sign-flip epoch >= 3 epochs later than majority in >= 70% of seeds).
    """

    def __init__(
        self,
        loss_history: np.ndarray,
        kappa_threshold: float = -0.002,
        consecutive_epochs: int = 2,
    ) -> None:
        """Initialize analyzer with loss trajectory data.

        Args:
            loss_history: Per-sample loss matrix, shape (N, num_epochs) = (4795, 20)
            kappa_threshold: Curvature threshold for stabilization detection.
                             Default -0.002 marks transition from convex to stable.
            consecutive_epochs: Number of consecutive epochs above threshold
                               required to confirm stabilization. Default 2.
        """
        self.loss_history = loss_history
        self.kappa_threshold = kappa_threshold
        self.consecutive_epochs = consecutive_epochs
        self.num_samples, self.num_epochs = loss_history.shape

    def normalize_loss(self) -> np.ndarray:
        """Normalize loss by initial value for scale invariance.

        L_norm[t] = L[t] / (L[0] + epsilon)

        Returns:
            Normalized loss matrix, shape (N, num_epochs)
        """
        L = self.loss_history
        L_norm = L / (L[:, 0:1] + 1e-8)
        return L_norm

    def compute_curvature(self, sigma: float = 1.0) -> np.ndarray:
        """Compute second derivative of normalized loss curves.

        Uses optional Gaussian smoothing followed by central differences:
        kappa[t] = L[t+1] - 2*L[t] + L[t-1]

        Args:
            sigma: Gaussian smoothing parameter. Default 1.0.
                   Set to 0 to disable smoothing.

        Returns:
            Curvature matrix, shape (N, num_epochs - 2)
        """
        L_norm = self.normalize_loss()

        # Apply Gaussian smoothing to reduce noise
        if sigma > 0:
            L_smooth = gaussian_filter1d(L_norm, sigma=sigma, axis=1)
        else:
            L_smooth = L_norm

        # Central differences for second derivative
        # kappa[t] = L[t+1] - 2*L[t] + L[t-1] for t in 1..num_epochs-2
        curvature = L_smooth[:, 2:] - 2 * L_smooth[:, 1:-1] + L_smooth[:, :-2]

        return curvature

    def detect_sign_flip_epoch(self, curvature: np.ndarray) -> np.ndarray:
        """Detect sign-flip epoch for each sample.

        Sign-flip epoch is the first epoch where curvature exceeds the
        threshold for `consecutive_epochs` consecutive epochs, indicating
        transition from convex (negative curvature) to stable (near-zero).

        Args:
            curvature: Curvature matrix, shape (N, E-2) where E = num_epochs

        Returns:
            Sign-flip epochs array, shape (N,). Values range from 1 to max_epoch.
            If no sign-flip detected, value is num_epochs + 2 (never stabilized).
        """
        N, E = curvature.shape
        # Default: never stabilized (set to num_epochs + 2)
        sign_flip_epochs = np.full(N, self.num_epochs + 2, dtype=np.int32)

        # Check each sample
        for i in range(N):
            for t in range(E - self.consecutive_epochs + 1):
                # Check if curvature > threshold for consecutive epochs
                window = curvature[i, t:t + self.consecutive_epochs]
                if np.all(window > self.kappa_threshold):
                    # +1 for 1-indexed epochs, +1 for offset from curvature start
                    sign_flip_epochs[i] = t + 2  # epoch index in original timeline
                    break

        return sign_flip_epochs

    def compute_timing_gap(
        self,
        group_labels: np.ndarray,
        sigma: float = 1.0,
    ) -> Dict[str, Any]:
        """Compute timing gap between minority and majority groups.

        Minority groups: G2 (group_id=1) and G3 (group_id=2)
        - Landbirds on water background
        - Waterbirds on land background

        Majority groups: G1 (group_id=0) and G4 (group_id=3)
        - Landbirds on land background
        - Waterbirds on water background

        Args:
            group_labels: Group labels array, shape (N,), values 0-3
            sigma: Gaussian smoothing parameter for curvature computation

        Returns:
            Dictionary with:
                timing_gap: float (median_minority - median_majority)
                minority_median_epoch: float
                majority_median_epoch: float
                minority_sign_flips: np.ndarray (N_minority,)
                majority_sign_flips: np.ndarray (N_majority,)
                minority_count: int
                majority_count: int
        """
        # Compute curvature and sign-flip epochs
        curvature = self.compute_curvature(sigma=sigma)
        sign_flip_epochs = self.detect_sign_flip_epoch(curvature)

        # Minority groups: G2 (group_id=1) and G3 (group_id=2)
        # These are samples where spurious correlation doesn't hold
        minority_mask = (group_labels == 1) | (group_labels == 2)
        majority_mask = ~minority_mask

        minority_sign_flips = sign_flip_epochs[minority_mask]
        majority_sign_flips = sign_flip_epochs[majority_mask]

        minority_median = float(np.median(minority_sign_flips))
        majority_median = float(np.median(majority_sign_flips))
        timing_gap = minority_median - majority_median

        return {
            'timing_gap': timing_gap,
            'minority_median_epoch': minority_median,
            'majority_median_epoch': majority_median,
            'minority_sign_flips': minority_sign_flips,
            'majority_sign_flips': majority_sign_flips,
            'minority_count': int(np.sum(minority_mask)),
            'majority_count': int(np.sum(majority_mask)),
            'curvature': curvature,
            'sign_flip_epochs': sign_flip_epochs,
        }


def verify_curvature_mechanism(
    loss_history: np.ndarray,
    group_labels: np.ndarray,
    sigma: float = 1.0,
) -> bool:
    """Verify curvature mechanism is working correctly.

    Performs sanity checks on curvature computation and sign-flip detection.

    Args:
        loss_history: Per-sample loss matrix, shape (N, num_epochs)
        group_labels: Group labels array, shape (N,)
        sigma: Gaussian smoothing parameter

    Returns:
        True if all checks pass, raises AssertionError otherwise
    """
    analyzer = CurvatureTimingAnalyzer(loss_history)

    # Check curvature shape
    curvature = analyzer.compute_curvature(sigma=sigma)
    expected_shape = (loss_history.shape[0], loss_history.shape[1] - 2)
    assert curvature.shape == expected_shape, \
        f"Curvature shape mismatch: {curvature.shape} vs expected {expected_shape}"
    print(f"  Curvature computed: shape {curvature.shape}")

    # Check curvature values are reasonable
    assert not np.all(curvature == 0), "Curvature is all zeros - mechanism not activating"
    assert not np.any(np.isnan(curvature)), "Curvature contains NaN - numerical issue"
    print(f"  Curvature values valid: mean={curvature.mean():.6f}, std={curvature.std():.6f}")

    # Check sign-flip detection
    sign_flip_epochs = analyzer.detect_sign_flip_epoch(curvature)
    detected_count = np.sum(sign_flip_epochs < analyzer.num_epochs + 2)
    print(f"  Sign-flip detected for {detected_count}/{len(sign_flip_epochs)} samples")

    # Check group comparison
    results = analyzer.compute_timing_gap(group_labels, sigma=sigma)
    print(f"  Timing gap computed: {results['timing_gap']:.2f} epochs")
    print(f"    Minority median: {results['minority_median_epoch']:.2f}")
    print(f"    Majority median: {results['majority_median_epoch']:.2f}")

    return True
