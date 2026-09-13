"""Symbolic Signal Extractor for h-m3.

Extracts symbolic divergence signals (state collisions, exponential growth)
from proof search trajectories.
"""

import numpy as np
from typing import List, Dict, Any


class SymbolicSignalExtractor:
    """Extract symbolic divergence signals from proof states."""

    def __init__(self, growth_window: int = 10):
        """Initialize extractor.

        Args:
            growth_window: Number of states to use for growth trend fitting
        """
        self.growth_window = growth_window

    def extract_signals(self, proof_states: List[Any], search_tree: Any) -> Dict[str, float]:
        """Extract symbolic signals from proof search trajectory.

        Args:
            proof_states: List of proof states from search
            search_tree: SearchTree object with collision tracking

        Returns:
            Dictionary with 'state_collisions' and 'exponential_growth_rate'
        """
        collisions = self._count_state_collisions(search_tree)
        growth_rate = self._fit_exponential_growth(proof_states)

        return {
            'state_collisions': collisions,
            'exponential_growth_rate': growth_rate
        }

    def _count_state_collisions(self, search_tree: Any) -> int:
        """Count state hash collisions using SearchTree.

        Args:
            search_tree: SearchTree with get_collision_count() method

        Returns:
            Number of hash collisions
        """
        if hasattr(search_tree, 'get_collision_count'):
            return search_tree.get_collision_count()
        return 0

    def _fit_exponential_growth(self, proof_states: List[Any]) -> float:
        """Fit exponential trend to proof state sizes.

        Algorithm:
        1. Extract state sizes (number of goals)
        2. Log-transform sizes
        3. Fit linear regression to log(size) vs time
        4. Return slope (exponential growth rate)

        Args:
            proof_states: List of proof states

        Returns:
            Exponential growth rate (slope in log space)
        """
        if len(proof_states) < 2:
            return 0.0

        # Extract state sizes
        sizes = []
        for state in proof_states[:self.growth_window]:
            try:
                if hasattr(state, 'goals'):
                    size = len(state.goals)
                elif hasattr(state, 'pp'):
                    size = len(str(state.pp))
                else:
                    size = len(str(state))
                sizes.append(max(size, 1))
            except:
                sizes.append(1)

        if len(sizes) < 2:
            return 0.0

        # Log-transform and fit linear regression
        t = np.arange(len(sizes))
        log_sizes = np.log(np.array(sizes))

        try:
            # polyfit: returns [slope, intercept]
            coeffs = np.polyfit(t, log_sizes, 1)
            return float(coeffs[0])
        except:
            return 0.0
