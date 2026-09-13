"""Distribution divergence analysis module."""

from scipy.stats import entropy
import numpy as np
import pandas as pd
from typing import Dict, List


class DistributionDivergenceAnalyzer:
    """Analyze feature distribution divergence across benchmarks."""

    def __init__(self, feature_df: pd.DataFrame):
        """Initialize with feature DataFrame."""
        self.feature_df = feature_df
        self.divergences: Dict[str, float] = {}

    def compute_kl_divergence(
        self, bench1: str, bench2: str, feature: str = "pass@1", bins: int = 20
    ) -> float:
        """
        Compute KL divergence between feature distributions.

        Args:
            bench1: First benchmark name
            bench2: Second benchmark name
            feature: Feature to analyze
            bins: Number of histogram bins

        Returns:
            KL divergence value
        """
        # Extract feature values for each benchmark
        dist1 = self.feature_df[self.feature_df['benchmark'] == bench1][feature].values
        dist2 = self.feature_df[self.feature_df['benchmark'] == bench2][feature].values

        if len(dist1) < 2 or len(dist2) < 2:
            return np.nan

        # Create histograms with common bins
        min_val = min(dist1.min(), dist2.min())
        max_val = max(dist1.max(), dist2.max())
        bin_edges = np.linspace(min_val, max_val, bins + 1)

        hist1, _ = np.histogram(dist1, bins=bin_edges, density=True)
        hist2, _ = np.histogram(dist2, bins=bin_edges, density=True)

        # Add epsilon for numerical stability
        epsilon = 1e-10
        hist1 = hist1 + epsilon
        hist2 = hist2 + epsilon

        # Normalize to probability distributions
        hist1 = hist1 / hist1.sum()
        hist2 = hist2 / hist2.sum()

        # Compute KL divergence
        kl_div = entropy(pk=hist1, qk=hist2)

        return float(kl_div)

    def compute_all_divergences(
        self, benchmarks: List[str], features: List[str], bins: int = 20
    ) -> Dict[str, Dict[str, float]]:
        """
        Compute KL divergences for all benchmark pairs and features.

        Args:
            benchmarks: List of benchmark names
            features: List of features to analyze
            bins: Number of histogram bins

        Returns:
            Nested dictionary: {pair_name: {feature: kl_value}}
        """
        results = {}

        for i, bench1 in enumerate(benchmarks):
            for bench2 in benchmarks[i+1:]:
                pair_name = f"{bench1}-{bench2}"
                results[pair_name] = {}

                for feature in features:
                    kl_div = self.compute_kl_divergence(bench1, bench2, feature, bins)
                    results[pair_name][feature] = kl_div

        return results

    def aggregate_divergence_scores(
        self, divergence_results: Dict[str, Dict[str, float]]
    ) -> Dict[str, float]:
        """
        Aggregate divergence scores across features.

        Args:
            divergence_results: Results from compute_all_divergences

        Returns:
            Dictionary mapping pair_name to mean divergence
        """
        aggregated = {}

        for pair_name, feature_divs in divergence_results.items():
            # Average divergence across features
            valid_divs = [v for v in feature_divs.values() if not np.isnan(v)]
            if valid_divs:
                aggregated[pair_name] = np.mean(valid_divs)
            else:
                aggregated[pair_name] = np.nan

        return aggregated
