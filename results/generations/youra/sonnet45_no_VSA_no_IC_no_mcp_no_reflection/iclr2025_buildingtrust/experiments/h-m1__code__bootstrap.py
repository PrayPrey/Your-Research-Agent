import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import squareform
from scipy.stats import spearmanr
from typing import Tuple


class BootstrapClusterValidator:
    def __init__(
        self,
        benchmark_data: pd.DataFrame,
        optimal_k: int,
        n_iterations: int = 1000,
        random_seed: int = 42
    ):
        self.data = benchmark_data
        self.k = optimal_k
        self.n_iter = n_iterations
        self.seed = random_seed

    def run_bootstrap(self) -> np.ndarray:
        # [3, 3] co-occurrence percentages
        np.random.seed(self.seed)
        n_benchmarks = 3
        co_occurrence = np.zeros((n_benchmarks, n_benchmarks))

        for _ in range(self.n_iter):
            indices = np.random.choice(len(self.data), size=len(self.data), replace=True)
            bootstrap_df = self.data.iloc[indices]

            corr_matrix = self._compute_correlation(bootstrap_df)
            dist_matrix = 1 - np.abs(corr_matrix)
            condensed = squareform(dist_matrix)
            Z = linkage(condensed, method='ward')
            labels = fcluster(Z, self.k, criterion='maxclust')

            for i in range(n_benchmarks):
                for j in range(n_benchmarks):
                    if labels[i] == labels[j]:
                        co_occurrence[i, j] += 1

        consistency_matrix = (co_occurrence / self.n_iter) * 100
        return consistency_matrix

    def _compute_correlation(self, df: pd.DataFrame) -> np.ndarray:
        # [3, 3] correlation matrix
        benchmark_cols = ['truthfulqa_score', 'advbench_score', 'bold_score']
        corr_matrix = np.zeros((3, 3))
        for i, col_i in enumerate(benchmark_cols):
            for j, col_j in enumerate(benchmark_cols):
                if i == j:
                    corr_matrix[i, j] = 1.0
                else:
                    corr_matrix[i, j] = spearmanr(df[col_i], df[col_j])[0]
        return corr_matrix

    def compute_consistency_matrix(self, consistency_matrix: np.ndarray) -> Tuple[np.ndarray, float]:
        # (consistency_matrix, mean_consistency) where mean_consistency >= 80.0 for gate pass
        n = consistency_matrix.shape[0]
        upper_tri = np.triu_indices(n, k=1)
        mean_consistency = np.mean(consistency_matrix[upper_tri])
        return consistency_matrix, mean_consistency
