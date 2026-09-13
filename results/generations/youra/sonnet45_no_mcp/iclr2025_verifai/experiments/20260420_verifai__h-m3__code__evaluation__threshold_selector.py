"""Threshold Selector for h-m3.

Selects thresholds for each signal type using median strategy from timeout group.
"""

import numpy as np
from typing import Dict, List, Any


class ThresholdSelector:
    """Select signal thresholds using median strategy from timeout group."""

    def __init__(self, fallback_thresholds: Dict[str, float] = None):
        """Initialize selector.

        Args:
            fallback_thresholds: Default thresholds if timeout group is empty
        """
        self.fallback_thresholds = fallback_thresholds or {
            'confidence_variance': 0.25,  # From h-m1
            'state_collisions': 2,
            'exponential_growth': 0.5,
            'backtrack_freq': 0.3
        }

    def select_thresholds(self, signals_list: List[Dict[str, float]],
                         labels: List[int]) -> Dict[str, float]:
        """Select thresholds using median of timeout group.

        Args:
            signals_list: List of signal dictionaries
            labels: List of labels (0=success, 1=timeout)

        Returns:
            Dictionary with selected thresholds for each signal
        """
        # Filter timeout group
        timeout_signals = [s for s, label in zip(signals_list, labels) if label == 1]

        if len(timeout_signals) == 0:
            print("⚠ No timeout examples, using fallback thresholds")
            return self.fallback_thresholds.copy()

        # Calculate median for each signal
        thresholds = {}

        # Confidence variance
        conf_values = [s.get('confidence_variance', 0.0) for s in timeout_signals]
        thresholds['confidence_variance'] = float(np.median(conf_values))

        # State collisions
        coll_values = [s.get('state_collisions', 0) for s in timeout_signals]
        thresholds['state_collisions'] = float(np.median(coll_values))

        # Exponential growth
        growth_values = [s.get('exponential_growth', 0.0) for s in timeout_signals]
        thresholds['exponential_growth'] = float(np.median(growth_values))

        # Backtrack frequency
        back_values = [s.get('backtrack_freq', 0.0) for s in timeout_signals]
        thresholds['backtrack_freq'] = float(np.median(back_values))

        return thresholds

    def validate_thresholds(self, thresholds: Dict[str, float]) -> bool:
        """Validate threshold values are reasonable.

        Args:
            thresholds: Threshold dictionary

        Returns:
            True if all thresholds are valid
        """
        # Check all required keys present
        required_keys = ['confidence_variance', 'state_collisions',
                        'exponential_growth', 'backtrack_freq']

        for key in required_keys:
            if key not in thresholds:
                return False

            # Check value is non-negative
            if thresholds[key] < 0:
                return False

        return True
