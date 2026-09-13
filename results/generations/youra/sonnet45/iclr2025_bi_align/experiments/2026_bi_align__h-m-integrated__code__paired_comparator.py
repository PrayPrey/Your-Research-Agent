"""Paired comparison module for linguistic markers.

This module implements paired t-test, Cohen's d, and primary gate evaluation.
"""

import sys
import os
from typing import List, Tuple, Dict
import numpy as np
from scipy.stats import ttest_rel

# Add h-e1 code path
h_e1_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../h-e1/code')
)
if h_e1_path not in sys.path:
    sys.path.insert(0, h_e1_path)

from extractor import LinguisticMarkerExtractor


class PairedComparator:
    """Comparator for paired linguistic marker analysis."""

    def __init__(self, extractor: LinguisticMarkerExtractor):
        """Initialize comparator.

        Args:
            extractor: H-E1 linguistic marker extractor
        """
        self.extractor = extractor

    def extract_paired_features(
        self, pairs: List[Tuple[str, str]]
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Extract features from pairs.

        Args:
            pairs: List of (chosen_text, rejected_text) tuples

        Returns:
            Tuple of (chosen_features [N, 3], rejected_features [N, 3])
            Features: [modal_freq, hedging_freq, alt_freq]
        """
        chosen_features = []
        rejected_features = []

        print(f"\nExtracting features from {len(pairs)} pairs...")

        for idx, (chosen_text, rejected_text) in enumerate(pairs):
            # Extract features for chosen response
            chosen_feat = self.extractor.extract_all_features(chosen_text)
            chosen_features.append([
                chosen_feat['modal_freq'],
                chosen_feat['hedging_freq'],
                chosen_feat['alt_freq']
            ])

            # Extract features for rejected response
            rejected_feat = self.extractor.extract_all_features(rejected_text)
            rejected_features.append([
                rejected_feat['modal_freq'],
                rejected_feat['hedging_freq'],
                rejected_feat['alt_freq']
            ])

            if (idx + 1) % 1000 == 0:
                print(f"  Processed {idx + 1}/{len(pairs)} pairs...")

        chosen_array = np.array(chosen_features)
        rejected_array = np.array(rejected_features)

        print(f"✓ Feature extraction complete")
        print(f"  Chosen features shape: {chosen_array.shape}")
        print(f"  Rejected features shape: {rejected_array.shape}")

        return chosen_array, rejected_array

    def paired_ttest(
        self, chosen: np.ndarray, rejected: np.ndarray
    ) -> Dict[str, float]:
        """Conduct paired t-test on modal verbs (primary marker).

        Args:
            chosen: Chosen features [N, 3]
            rejected: Rejected features [N, 3]

        Returns:
            Dictionary with t_stat and p_value
        """
        # Paired t-test on modal verbs (column 0)
        t_stat, p_value = ttest_rel(chosen[:, 0], rejected[:, 0])

        return {
            't_stat': float(t_stat),
            'p_value': float(p_value)
        }

    def cohens_d_paired(
        self, chosen: np.ndarray, rejected: np.ndarray
    ) -> float:
        """Compute Cohen's d for paired samples.

        Args:
            chosen: Chosen features [N, 3]
            rejected: Rejected features [N, 3]

        Returns:
            Cohen's d effect size (negative if chosen < rejected)
        """
        # Compute differences (chosen - rejected) for modal verbs
        differences = chosen[:, 0] - rejected[:, 0]

        # Cohen's d for paired samples
        mean_diff = np.mean(differences)
        std_diff = np.std(differences, ddof=1)

        if std_diff == 0:
            return 0.0

        cohens_d = mean_diff / std_diff

        return float(cohens_d)

    def check_primary_gate(
        self, cohens_d: float, p_value: float, threshold_d: float = 0.15,
        threshold_p: float = 0.05
    ) -> bool:
        """Check primary gate criteria.

        Gate: |d| >= 0.15 AND p < 0.05 AND d < 0 (chosen < rejected)

        Args:
            cohens_d: Cohen's d effect size
            p_value: p-value from paired t-test
            threshold_d: Cohen's d threshold
            threshold_p: p-value threshold

        Returns:
            True if primary gate passed
        """
        magnitude_pass = abs(cohens_d) >= threshold_d
        significance_pass = p_value < threshold_p
        direction_pass = cohens_d < 0  # chosen < rejected

        return magnitude_pass and significance_pass and direction_pass
