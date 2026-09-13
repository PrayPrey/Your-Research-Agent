"""Hybrid Termination Detector for h-m3.

Three-signal hybrid detector with k-of-n voting logic.
"""

import sys
from pathlib import Path
from typing import Dict, Any

# Add signals directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "signals"))

from symbolic_extractor import SymbolicSignalExtractor


class HybridTerminationDetector:
    """Three-signal hybrid detector with k-of-n voting."""

    def __init__(self, thresholds: Dict[str, float], voting_k: int = 2):
        """Initialize detector.

        Args:
            thresholds: Dictionary with thresholds for each signal type
            voting_k: Number of signals that must trigger (default: 2 of 3)
        """
        self.thresholds = thresholds
        self.voting_k = voting_k
        self.symbolic_extractor = SymbolicSignalExtractor()

    def extract_all_signals(self, result: Dict[str, Any]) -> Dict[str, float]:
        """Extract all three signal types from experiment result.

        Args:
            result: From ExtendedTimeoutRunnerWithTree with:
                - confidence_variance: float
                - proof_states: list
                - search_tree: SearchTree

        Returns:
            Dictionary with all four signals:
                - confidence_variance
                - state_collisions
                - exponential_growth
                - backtrack_freq
        """
        # Signal 1: Confidence variance (from result)
        confidence_variance = result.get('confidence_variance', 0.0)

        # Signal 2 & 3: Symbolic signals (NEW)
        symbolic_signals = self.symbolic_extractor.extract_signals(
            result.get('proof_states', []),
            result.get('search_tree')
        )

        # Signal 4: Search tree backtrack frequency (from result)
        search_tree = result.get('search_tree')
        backtrack_count = 0
        if search_tree and hasattr(search_tree, 'get_backtrack_count'):
            backtrack_count = search_tree.get_backtrack_count()

        # Calculate backtrack frequency (normalize by total states)
        num_states = len(result.get('proof_states', []))
        backtrack_freq = backtrack_count / max(num_states, 1)

        return {
            'confidence_variance': confidence_variance,
            'state_collisions': symbolic_signals['state_collisions'],
            'exponential_growth': symbolic_signals['exponential_growth_rate'],
            'backtrack_freq': backtrack_freq
        }

    def predict(self, signals: Dict[str, float]) -> bool:
        """Voting-based termination decision.

        Args:
            signals: Dictionary with all signal values

        Returns:
            True if should terminate (at least k of 3 signals trigger)
        """
        # Check each signal against threshold
        confidence_alert = self._check_confidence_alert(signals)
        symbolic_alert = self._check_symbolic_alert(signals)
        search_alert = self._check_search_alert(signals)

        # Count votes
        votes = sum([confidence_alert, symbolic_alert, search_alert])

        # Return decision
        return votes >= self.voting_k

    def _check_confidence_alert(self, signals: Dict[str, float]) -> bool:
        """Check if confidence signal triggers.

        Args:
            signals: Signal dictionary

        Returns:
            True if variance > threshold
        """
        variance = signals.get('confidence_variance', 0.0)
        threshold = self.thresholds.get('confidence_variance', 0.25)
        return variance > threshold

    def _check_symbolic_alert(self, signals: Dict[str, float]) -> bool:
        """Check if symbolic signals trigger.

        Args:
            signals: Signal dictionary

        Returns:
            True if collisions OR growth exceeds threshold
        """
        collisions = signals.get('state_collisions', 0)
        growth = signals.get('exponential_growth', 0.0)

        collision_thresh = self.thresholds.get('state_collisions', 2)
        growth_thresh = self.thresholds.get('exponential_growth', 0.5)

        return (collisions > collision_thresh) or (growth > growth_thresh)

    def _check_search_alert(self, signals: Dict[str, float]) -> bool:
        """Check if search tree signal triggers.

        Args:
            signals: Signal dictionary

        Returns:
            True if backtrack_freq > threshold
        """
        backtrack_freq = signals.get('backtrack_freq', 0.0)
        threshold = self.thresholds.get('backtrack_freq', 0.3)
        return backtrack_freq > threshold
