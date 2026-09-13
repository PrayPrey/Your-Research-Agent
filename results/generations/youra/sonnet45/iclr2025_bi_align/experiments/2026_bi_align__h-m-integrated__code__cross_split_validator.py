"""Cross-split validation module.

This module implements per-split replication analysis.
"""

from typing import Dict, List, Tuple, Any
import numpy as np


class CrossSplitValidator:
    """Validator for cross-split replication."""

    def __init__(self, comparator):
        """Initialize validator.

        Args:
            comparator: PairedComparator instance
        """
        self.comparator = comparator

    def validate_per_split(
        self, split_pairs: Dict[str, List[Tuple[str, str]]]
    ) -> Dict[str, Dict[str, Any]]:
        """Validate per split.

        Args:
            split_pairs: Dict mapping split names to list of pairs

        Returns:
            Dictionary with split results
            {'split_name': {'cohens_d': float, 'p_value': float, 'pass': bool}}
        """
        results = {}

        print("\n=== Cross-Split Validation ===")

        for split_name, pairs in split_pairs.items():
            print(f"\nValidating {split_name} split ({len(pairs)} pairs)...")

            # Extract features for this split
            chosen_features, rejected_features = self.comparator.extract_paired_features(pairs)

            # Compute paired t-test
            ttest_result = self.comparator.paired_ttest(chosen_features, rejected_features)

            # Compute Cohen's d
            cohens_d = self.comparator.cohens_d_paired(chosen_features, rejected_features)

            # Check if passes primary criteria
            passes = self.comparator.check_primary_gate(cohens_d, ttest_result['p_value'])

            results[split_name] = {
                'cohens_d': cohens_d,
                'p_value': ttest_result['p_value'],
                't_stat': ttest_result['t_stat'],
                'n_pairs': len(pairs),
                'pass': passes
            }

            print(f"  Cohen's d: {cohens_d:.4f}")
            print(f"  p-value: {ttest_result['p_value']:.6f}")
            print(f"  Status: {'PASS' if passes else 'FAIL'}")

        return results

    def count_passing_splits(self, split_results: Dict[str, Dict]) -> int:
        """Count splits that pass primary criteria.

        Args:
            split_results: Results from validate_per_split

        Returns:
            Number of passing splits
        """
        return sum(1 for result in split_results.values() if result['pass'])

    def check_tertiary_gate(
        self, passing_count: int, total_splits: int, min_passing: int = 2
    ) -> bool:
        """Check tertiary gate: sufficient replication.

        Args:
            passing_count: Number of splits that passed
            total_splits: Total number of splits tested
            min_passing: Minimum required passing splits

        Returns:
            True if tertiary gate passed
        """
        return passing_count >= min_passing
