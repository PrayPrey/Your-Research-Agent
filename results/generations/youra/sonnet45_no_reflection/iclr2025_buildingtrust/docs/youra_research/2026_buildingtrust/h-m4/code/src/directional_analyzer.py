"""
Directional Replication Analyzer for H-M4
Computes correlation directions and replication rates across model families
"""

import numpy as np
from scipy.stats import pearsonr
from typing import Dict, List, Tuple
import json


class DirectionalReplicationAnalyzer:
    """Analyzes directional replication of correlation patterns across model families"""

    def __init__(self, dimensions: List[str], direction_thresholds: Dict):
        self.dimensions = dimensions
        self.direction_thresholds = direction_thresholds
        self.results = {}

    def compute_family_correlations(
        self,
        family_deltas: Dict[str, List[float]]
    ) -> Dict[str, Tuple[float, float, str]]:
        """
        Compute correlations for all dimension pairs in one family

        Args:
            family_deltas: {dimension: [delta1, delta2, ..., delta5]} across 5 seeds

        Returns:
            {dim_pair: (correlation, p_value, direction)}
        """
        correlations = {}

        # Get all dimension pairs
        for i in range(len(self.dimensions)):
            for j in range(i + 1, len(self.dimensions)):
                dim1, dim2 = self.dimensions[i], self.dimensions[j]
                pair_name = f"{dim1}-{dim2}"

                deltas1 = family_deltas[dim1]
                deltas2 = family_deltas[dim2]

                # Compute Pearson correlation
                if len(deltas1) >= 3 and len(deltas2) >= 3:
                    r, p = pearsonr(deltas1, deltas2)
                    direction = self.classify_direction(r)
                    correlations[pair_name] = (r, p, direction)
                else:
                    correlations[pair_name] = (0.0, 1.0, "neutral")

        return correlations

    def classify_direction(self, r: float) -> str:
        """Classify correlation direction based on thresholds"""
        if r > self.direction_thresholds["positive"]:
            return "positive"
        elif r < self.direction_thresholds["negative"]:
            return "negative"
        else:
            return "neutral"

    def compute_replication_rate(
        self,
        all_family_results: Dict[str, Dict]
    ) -> Dict[str, Dict]:
        """
        Compute replication rate for each dimension pair across families

        Args:
            all_family_results: {family_name: {dim_pair: (r, p, direction)}}

        Returns:
            {dim_pair: {majority_direction, replication_rate, matching_families}}
        """
        replication_results = {}

        # Get all dimension pairs
        first_family = list(all_family_results.values())[0]
        dimension_pairs = list(first_family.keys())

        for dim_pair in dimension_pairs:
            # Collect directions from all families
            directions = []
            for family_name, family_results in all_family_results.items():
                if dim_pair in family_results:
                    _, _, direction = family_results[dim_pair]
                    directions.append((family_name, direction))

            # Find majority direction
            direction_counts = {}
            for family, direction in directions:
                direction_counts[direction] = direction_counts.get(direction, 0) + 1

            majority_direction = max(direction_counts, key=direction_counts.get)
            majority_count = direction_counts[majority_direction]

            # Compute replication rate
            total_families = len(directions)
            replication_rate = majority_count / total_families if total_families > 0 else 0.0

            # Get matching families
            matching_families = [
                family for family, direction in directions
                if direction == majority_direction
            ]

            replication_results[dim_pair] = {
                "majority_direction": majority_direction,
                "replication_rate": replication_rate,
                "replication_count": majority_count,
                "total_families": total_families,
                "matching_families": matching_families,
                "gate_passed": replication_rate >= 0.6  # ≥3/5 threshold
            }

        return replication_results

    def check_gate_criterion(
        self,
        replication_results: Dict[str, Dict],
        min_pairs: int = 1
    ) -> Tuple[bool, Dict]:
        """
        Check if SHOULD_WORK gate is satisfied

        Gate: ≥3/5 models show same direction for at least one dimension pair

        Returns:
            (gate_passed, summary)
        """
        passed_pairs = [
            pair for pair, results in replication_results.items()
            if results["gate_passed"]
        ]

        gate_passed = len(passed_pairs) >= min_pairs

        summary = {
            "gate_passed": gate_passed,
            "passed_pairs": passed_pairs,
            "total_pairs": len(replication_results),
            "replication_rates": {
                pair: results["replication_rate"]
                for pair, results in replication_results.items()
            }
        }

        return gate_passed, summary

    def save_results(self, filepath: str, all_results: Dict):
        """Save analysis results to JSON"""
        with open(filepath, 'w') as f:
            json.dump(all_results, f, indent=2)
        print(f"Results saved to {filepath}")
