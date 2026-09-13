"""Benchmark correlation analysis module."""

from scipy.stats import spearmanr
import pandas as pd
import numpy as np
from typing import Dict, Tuple, List


class BenchmarkCorrelationAnalyzer:
    """Analyze model ranking correlation across benchmarks."""

    def __init__(self, feature_df: pd.DataFrame):
        """Initialize with feature DataFrame from h-e1."""
        self.feature_df = feature_df
        self.correlations: Dict[str, Dict[str, float]] = {}

    def compute_ranking_correlation(
        self, bench1: str, bench2: str, feature: str = 'pass@1'
    ) -> Tuple[float, float]:
        """
        Compute Spearman correlation between model rankings.

        Args:
            bench1: First benchmark name
            bench2: Second benchmark name
            feature: Feature to use for ranking (default: 'pass@1')

        Returns:
            (rho, p_value) - Correlation coefficient and significance
        """
        # Extract scores for each benchmark
        scores1 = self.feature_df[self.feature_df['benchmark'] == bench1].set_index('model')[feature]
        scores2 = self.feature_df[self.feature_df['benchmark'] == bench2].set_index('model')[feature]

        # Find common models
        common_models = scores1.index.intersection(scores2.index)

        if len(common_models) < 2:
            return np.nan, np.nan

        # Align and compute correlation
        aligned1 = scores1.loc[common_models]
        aligned2 = scores2.loc[common_models]

        rho, p_value = spearmanr(aligned1, aligned2)

        return float(rho), float(p_value)

    def compute_all_pairwise_correlations(
        self, benchmarks: List[str], feature: str = 'pass@1'
    ) -> Dict[str, Dict[str, float]]:
        """
        Compute all pairwise benchmark correlations.

        Args:
            benchmarks: List of benchmark names
            feature: Feature to use for ranking

        Returns:
            Dictionary mapping "bench1-bench2" to {"rho": float, "p_value": float}
        """
        self.correlations = {}

        for i, bench1 in enumerate(benchmarks):
            for bench2 in benchmarks[i+1:]:
                rho, p_value = self.compute_ranking_correlation(bench1, bench2, feature)
                pair_name = f"{bench1}-{bench2}"
                self.correlations[pair_name] = {
                    'rho': rho,
                    'p_value': p_value
                }

        return self.correlations

    def get_correlation_matrix(self, benchmarks: List[str]) -> pd.DataFrame:
        """
        Get correlation matrix for visualization.

        Args:
            benchmarks: List of benchmark names

        Returns:
            DataFrame with benchmarks as rows/columns
        """
        n = len(benchmarks)
        matrix = np.eye(n)  # Diagonal is 1.0

        for i, bench1 in enumerate(benchmarks):
            for j, bench2 in enumerate(benchmarks):
                if i < j:
                    pair_name = f"{bench1}-{bench2}"
                    if pair_name in self.correlations:
                        rho = self.correlations[pair_name]['rho']
                        matrix[i, j] = rho
                        matrix[j, i] = rho

        return pd.DataFrame(matrix, index=benchmarks, columns=benchmarks)
