"""
Spearman Correlation Analysis Module for H-M1
Computes correlations between dataset features and method rankings.
"""

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from typing import Dict, List, Tuple


class SpearmanCorrelator:
    """Compute Spearman correlations between features and rankings."""

    def __init__(self, rho_threshold: float = 0.3, alpha: float = 0.05):
        """
        Args:
            rho_threshold: Minimum |ρ| for significance
            alpha: p-value threshold for statistical significance
        """
        self.rho_threshold = rho_threshold
        self.alpha = alpha

    def compute_correlation_matrix(
        self,
        features_df: pd.DataFrame,
        rankings_df: pd.DataFrame
    ) -> Dict[str, Dict[str, float]]:
        """
        Compute Spearman correlation for all (feature, method) pairs.

        Args:
            features_df: (N_benchmarks, N_features)
            rankings_df: (N_benchmarks, N_methods)

        Returns:
            Dictionary with structure:
            {
                "feature_vs_method": {
                    "rho": float,
                    "p_value": float,
                    "significant": bool
                }
            }
        """
        results = {}

        # Align indices
        common_idx = features_df.index.intersection(rankings_df.index)
        features_aligned = features_df.loc[common_idx]
        rankings_aligned = rankings_df.loc[common_idx]

        print(f"\n🔬 Computing correlations for {len(features_aligned)} benchmarks...")
        print(f"  Features: {len(features_aligned.columns)}")
        print(f"  Methods: {len(rankings_aligned.columns)}")

        total_pairs = len(features_aligned.columns) * len(rankings_aligned.columns)
        current_pair = 0

        for feature_name in features_aligned.columns:
            feature_values = features_aligned[feature_name].values

            # Skip if all values are identical
            if np.std(feature_values) == 0:
                continue

            for method_name in rankings_aligned.columns:
                ranking_values = rankings_aligned[method_name].values

                # Skip if all values are identical
                if np.std(ranking_values) == 0:
                    continue

                # Remove NaN pairs
                mask = ~(np.isnan(feature_values) | np.isnan(ranking_values))
                if mask.sum() < 3:  # Need at least 3 points
                    continue

                # Compute Spearman correlation
                try:
                    rho, p_value = spearmanr(
                        feature_values[mask],
                        ranking_values[mask]
                    )

                    # Handle NaN results
                    if np.isnan(rho) or np.isnan(p_value):
                        continue  # Skip pairs with invalid correlations

                    # Determine significance
                    significant = (abs(rho) > self.rho_threshold) and (p_value < self.alpha)

                    pair_name = f"{feature_name}_vs_{method_name}"
                    results[pair_name] = {
                        'rho': round(float(rho), 3),
                        'p_value': round(float(p_value), 4),
                        'significant': bool(significant),
                        'n_samples': int(mask.sum())
                    }
                except Exception as e:
                    # Skip pairs that fail correlation computation
                    continue

                current_pair += 1
                if current_pair % 10 == 0:
                    print(f"  Progress: {current_pair}/{total_pairs} pairs analyzed")

        print(f"✓ Correlation analysis complete: {len(results)} pairs analyzed")

        return results


class CorrelationReporter:
    """Generate reports and summaries from correlation results."""

    def __init__(self, correlations: Dict[str, Dict[str, float]]):
        """
        Args:
            correlations: Results from SpearmanCorrelator
        """
        self.correlations = correlations

    def count_significant_pairs(self) -> int:
        """Count pairs with significant correlation."""
        return sum(1 for r in self.correlations.values() if r['significant'])

    def get_top_correlations(self, n: int = 5) -> List[Tuple[str, Dict]]:
        """
        Get top N correlations by absolute |ρ|.

        Args:
            n: Number of top pairs to return

        Returns:
            List of (pair_name, correlation_data) sorted by |ρ|
        """
        sorted_pairs = sorted(
            self.correlations.items(),
            key=lambda x: abs(x[1]['rho']),
            reverse=True
        )
        return sorted_pairs[:n]

    def check_inverse_correlations(self) -> List[Tuple[str, Dict]]:
        """
        Find significant inverse correlations (ρ < -0.3, p < 0.05).

        Returns:
            List of (pair_name, correlation_data) with negative ρ
        """
        inverse = [
            (name, data)
            for name, data in self.correlations.items()
            if data['rho'] < -0.3 and data['p_value'] < 0.05
        ]
        return inverse

    def generate_summary_stats(self) -> Dict[str, float]:
        """
        Generate summary statistics.

        Returns:
            Dictionary with mean_rho, median_p, etc.
        """
        rhos = [r['rho'] for r in self.correlations.values()]
        p_values = [r['p_value'] for r in self.correlations.values()]

        return {
            'mean_rho': round(np.mean(rhos), 3),
            'median_rho': round(np.median(rhos), 3),
            'std_rho': round(np.std(rhos), 3),
            'mean_p_value': round(np.mean(p_values), 4),
            'median_p_value': round(np.median(p_values), 4),
            'significant_count': self.count_significant_pairs(),
            'total_pairs': len(self.correlations)
        }

    def determine_gate_result(self) -> str:
        """
        Determine gate result based on significant correlation count.

        Returns:
            "PASS", "PARTIAL", or "FAIL"
        """
        significant_count = self.count_significant_pairs()

        if significant_count >= 3:
            return "PASS"
        elif significant_count >= 1:
            return "PARTIAL"
        else:
            return "FAIL"
