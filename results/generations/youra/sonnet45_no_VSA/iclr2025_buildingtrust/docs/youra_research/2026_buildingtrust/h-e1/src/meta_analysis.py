"""Meta-analysis for CV-stability correlation hypothesis."""
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from scipy.stats import spearmanr, pearsonr


logger = logging.getLogger(__name__)


@dataclass
class AnalysisResults:
    """Container for meta-analysis results."""

    cv_per_benchmark: pd.DataFrame
    mean_rho_per_benchmark: pd.DataFrame
    pairwise_rho_matrix: pd.DataFrame
    pearson_r: float
    pearson_p: float
    ci_lower: float
    ci_upper: float
    gate_passed: bool


class BenchmarkMetaAnalysis:
    """Statistical meta-analysis for CV-stability correlation."""

    def __init__(self, min_models: int = 10, min_shared_models: int = 5):
        """Initialize meta-analysis.

        Args:
            min_models: Minimum models per benchmark
            min_shared_models: Minimum shared models for pairwise correlation
        """
        self.min_models = min_models
        self.min_shared_models = min_shared_models

    def analyze(self, benchmark_dict: Dict[str, pd.DataFrame]) -> AnalysisResults:
        """Execute complete meta-analysis pipeline.

        Args:
            benchmark_dict: {benchmark_name: DataFrame[model_name, score]}

        Returns:
            AnalysisResults with all statistics and gate decision
        """
        logger.info(f"Analyzing {len(benchmark_dict)} benchmarks...")

        # Step 1: Compute CV per benchmark
        cv_results = self._compute_all_cvs(benchmark_dict)

        # Step 2: Compute pairwise Spearman rho
        pairwise_matrix = self._compute_pairwise_rho_matrix(benchmark_dict)

        # Step 3: Compute mean rho per benchmark
        mean_rho_results = self._compute_mean_rho_per_benchmark(
            benchmark_dict, pairwise_matrix
        )

        # Step 4: Test CV-stability correlation
        r, p, ci_lower, ci_upper = self._test_cv_stability_correlation(
            cv_results, mean_rho_results
        )

        # Step 5: Gate decision
        gate_passed = (r < -0.5) and (p < 0.05)

        logger.info(f"Pearson r={r:.3f}, p={p:.4f}, Gate={'PASS' if gate_passed else 'FAIL'}")

        return AnalysisResults(
            cv_per_benchmark=cv_results,
            mean_rho_per_benchmark=mean_rho_results,
            pairwise_rho_matrix=pairwise_matrix,
            pearson_r=r,
            pearson_p=p,
            ci_lower=ci_lower,
            ci_upper=ci_upper,
            gate_passed=gate_passed
        )

    def compute_cv(self, scores: np.ndarray) -> float:
        """Compute coefficient of variation.

        Args:
            scores: Array of benchmark scores

        Returns:
            CV = std / mean
        """
        mean_score = np.mean(scores)
        std_score = np.std(scores, ddof=1)  # Sample std
        if mean_score == 0:
            return 0.0
        return std_score / mean_score

    def compute_cross_benchmark_rho(
        self,
        benchmark_a: pd.DataFrame,
        benchmark_b: pd.DataFrame
    ) -> Optional[float]:
        """Compute Spearman rho for shared models.

        Args:
            benchmark_a: DataFrame[model_name, score]
            benchmark_b: DataFrame[model_name, score]

        Returns:
            Spearman rho or None if insufficient overlap
        """
        # Find shared models
        shared = set(benchmark_a["model_name"]) & set(benchmark_b["model_name"])

        if len(shared) < self.min_shared_models:
            return None

        # Filter to shared models and align order
        a_shared = benchmark_a[benchmark_a["model_name"].isin(shared)]
        b_shared = benchmark_b[benchmark_b["model_name"].isin(shared)]

        a_shared = a_shared.sort_values("model_name").reset_index(drop=True)
        b_shared = b_shared.sort_values("model_name").reset_index(drop=True)

        # Compute Spearman correlation on ranks
        rho, _ = spearmanr(a_shared["score"], b_shared["score"])

        return rho

    def _compute_all_cvs(self, benchmark_dict: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Compute CV for all benchmarks.

        Args:
            benchmark_dict: {benchmark_name: DataFrame}

        Returns:
            DataFrame[benchmark_name, cv, mean, std, n_models]
        """
        results = []

        for name, df in benchmark_dict.items():
            scores = df["score"].values
            cv = self.compute_cv(scores)
            results.append({
                "benchmark_name": name,
                "cv": cv,
                "mean": np.mean(scores),
                "std": np.std(scores, ddof=1),
                "n_models": len(scores)
            })

        return pd.DataFrame(results)

    def _compute_pairwise_rho_matrix(
        self,
        benchmark_dict: Dict[str, pd.DataFrame]
    ) -> pd.DataFrame:
        """Compute pairwise Spearman rho matrix.

        Args:
            benchmark_dict: {benchmark_name: DataFrame}

        Returns:
            DataFrame[n_benchmarks x n_benchmarks] with pairwise rho values
        """
        names = list(benchmark_dict.keys())
        n = len(names)

        matrix = np.zeros((n, n))

        for i, name_a in enumerate(names):
            for j, name_b in enumerate(names):
                if i == j:
                    matrix[i, j] = 1.0
                elif i < j:
                    rho = self.compute_cross_benchmark_rho(
                        benchmark_dict[name_a],
                        benchmark_dict[name_b]
                    )
                    if rho is not None:
                        matrix[i, j] = rho
                        matrix[j, i] = rho
                    else:
                        matrix[i, j] = np.nan
                        matrix[j, i] = np.nan

        return pd.DataFrame(matrix, index=names, columns=names)

    def _compute_mean_rho_per_benchmark(
        self,
        benchmark_dict: Dict[str, pd.DataFrame],
        pairwise_matrix: pd.DataFrame
    ) -> pd.DataFrame:
        """Compute mean rho per benchmark.

        Args:
            benchmark_dict: {benchmark_name: DataFrame}
            pairwise_matrix: Pairwise rho matrix

        Returns:
            DataFrame[benchmark_name, mean_rho, n_pairs]
        """
        results = []
        names = list(benchmark_dict.keys())

        for name in names:
            # Get all pairwise rho values for this benchmark
            row = pairwise_matrix.loc[name]
            # Exclude self-correlation and NaN values
            rhos = row[(row.index != name) & (~row.isna())]

            results.append({
                "benchmark_name": name,
                "mean_rho": np.mean(rhos) if len(rhos) > 0 else np.nan,
                "n_pairs": len(rhos)
            })

        return pd.DataFrame(results)

    def _test_cv_stability_correlation(
        self,
        cv_results: pd.DataFrame,
        mean_rho_results: pd.DataFrame
    ) -> Tuple[float, float, float, float]:
        """Test H-E1: Pearson correlation between CV and mean rho.

        Args:
            cv_results: DataFrame with cv column
            mean_rho_results: DataFrame with mean_rho column

        Returns:
            (r, p, ci_lower, ci_upper)
        """
        # Merge on benchmark_name
        merged = cv_results.merge(mean_rho_results, on="benchmark_name")

        # Remove any NaN values
        merged = merged.dropna(subset=["cv", "mean_rho"])

        cv_values = merged["cv"].values
        rho_values = merged["mean_rho"].values

        # Pearson correlation
        r, p = pearsonr(cv_values, rho_values)

        # Compute 95% confidence interval using Fisher z-transformation
        n = len(cv_values)
        z = np.arctanh(r)
        se = 1 / np.sqrt(n - 3)
        z_lower = z - 1.96 * se
        z_upper = z + 1.96 * se
        ci_lower = np.tanh(z_lower)
        ci_upper = np.tanh(z_upper)

        return r, p, ci_lower, ci_upper
