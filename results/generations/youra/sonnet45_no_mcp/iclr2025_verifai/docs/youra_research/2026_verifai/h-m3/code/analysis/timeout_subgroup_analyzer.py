"""
Timeout Subgroup Analyzer for h-m2
Analyzes variance differences between divergent vs. difficult timeout groups.
"""

import sys
from pathlib import Path
from typing import List, Dict, Tuple, Any
import numpy as np

# Add h-m1 to path for base class (only if not already there)
h_m1_path = Path(__file__).parent.parent.parent.parent / "h-m1" / "code"
if str(h_m1_path) not in sys.path:
    sys.path.append(str(h_m1_path))  # Use append to maintain priority


class TimeoutSubgroupAnalyzer:
    """
    Analyzes timeout subgroups (divergent vs. difficult) to test h-m2 hypothesis.

    Hypothesis: Divergent timeouts show higher confidence variance than difficult timeouts.

    Gate Condition: mean_variance(divergent) > mean_variance(difficult)
    """

    def __init__(self):
        pass

    def analyze_variance_by_divergence(
        self,
        timeout_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Separate timeout group by divergence classification and compare variance.

        Args:
            timeout_results: List of experiment results with:
                - "variance": float (from h-m1)
                - "is_divergent": bool (from divergence classifier)
                - "divergence_markers": dict

        Returns:
            {
                "divergent_group": {
                    "count": int,
                    "mean_variance": float,
                    "std_variance": float,
                    "variances": List[float]
                },
                "difficult_group": {
                    "count": int,
                    "mean_variance": float,
                    "std_variance": float,
                    "variances": List[float]
                },
                "gate_satisfied": bool
            }
        """
        # Separate by divergence classification
        divergent_group, difficult_group = self._separate_by_divergence(timeout_results)

        # Compute statistics for each group
        divergent_stats = self._compute_group_statistics(divergent_group)
        difficult_stats = self._compute_group_statistics(difficult_group)

        # Evaluate gate condition
        gate_satisfied = self.evaluate_gate(divergent_stats, difficult_stats)

        return {
            "divergent_group": divergent_stats,
            "difficult_group": difficult_stats,
            "gate_satisfied": gate_satisfied
        }

    def _separate_by_divergence(
        self,
        timeout_results: List[Dict[str, Any]]
    ) -> Tuple[List[Dict], List[Dict]]:
        """
        Separate timeout results into divergent vs. difficult groups.
        """
        divergent = [r for r in timeout_results if r.get("is_divergent", False)]
        difficult = [r for r in timeout_results if not r.get("is_divergent", False)]

        return divergent, difficult

    def _compute_group_statistics(self, group: List[Dict]) -> Dict[str, Any]:
        """
        Compute variance statistics for a group.
        """
        if not group:
            return {
                "count": 0,
                "mean_variance": 0.0,
                "std_variance": 0.0,
                "variances": []
            }

        variances = [r["variance"] for r in group]

        return {
            "count": len(group),
            "mean_variance": float(np.mean(variances)),
            "std_variance": float(np.std(variances)),
            "variances": variances
        }

    def evaluate_gate(
        self,
        divergent_stats: Dict[str, Any],
        difficult_stats: Dict[str, Any]
    ) -> bool:
        """
        Evaluate gate condition: mean_variance(divergent) > mean_variance(difficult).

        Returns:
            True if gate satisfied, False otherwise.
        """
        # Handle edge cases
        if divergent_stats["count"] == 0 or difficult_stats["count"] == 0:
            return False  # Cannot compare if either group is empty

        mean_divergent = divergent_stats["mean_variance"]
        mean_difficult = difficult_stats["mean_variance"]

        # Gate: divergent should have higher variance
        return mean_divergent > mean_difficult


def test_subgroup_analyzer():
    """Test timeout subgroup analysis."""
    print("Testing TimeoutSubgroupAnalyzer...")

    # Mock timeout results
    timeout_results = [
        {"variance": 0.4, "is_divergent": True},   # Divergent
        {"variance": 0.5, "is_divergent": True},   # Divergent
        {"variance": 0.2, "is_divergent": False},  # Difficult
        {"variance": 0.3, "is_divergent": False},  # Difficult
    ]

    analyzer = TimeoutSubgroupAnalyzer()
    result = analyzer.analyze_variance_by_divergence(timeout_results)

    print(f"Divergent group: n={result['divergent_group']['count']}, "
          f"mean_var={result['divergent_group']['mean_variance']:.3f}")
    print(f"Difficult group: n={result['difficult_group']['count']}, "
          f"mean_var={result['difficult_group']['mean_variance']:.3f}")
    print(f"Gate satisfied: {result['gate_satisfied']}")

    # Verify gate logic
    assert result['divergent_group']['mean_variance'] > result['difficult_group']['mean_variance']
    assert result['gate_satisfied'] == True

    print("✓ Test passed!")


if __name__ == "__main__":
    test_subgroup_analyzer()
