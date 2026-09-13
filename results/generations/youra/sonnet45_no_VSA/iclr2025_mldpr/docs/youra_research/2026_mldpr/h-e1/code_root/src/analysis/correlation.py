"""Statistical analysis for hypothesis testing."""
import logging
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.linear_model import LogisticRegression
from typing import Tuple, Dict


logger = logging.getLogger(__name__)


class ReproducibilityAnalyzer:
    """Statistical analysis for hypothesis testing."""

    def __init__(self, random_seed: int = 42):
        """Initialize analyzer.

        Args:
            random_seed: Random seed for reproducibility
        """
        self.random_seed = random_seed
        np.random.seed(random_seed)
        self.logistic_model = LogisticRegression(
            max_iter=1000,
            random_state=random_seed
        )

    def compute_spearman_correlation(
        self,
        df: pd.DataFrame
    ) -> Tuple[float, float, Tuple[float, float]]:
        """Primary analysis: Spearman's ρ.

        Args:
            df: DataFrame with doc_score and reproduced_within_12m columns

        Returns:
            Tuple of (rho, p_value, confidence_interval)
        """
        logger.info("Computing Spearman correlation...")

        rho, p_value = spearmanr(
            df['doc_score'],
            df['reproduced_within_12m']
        )

        logger.info(f"Spearman ρ = {rho:.3f}, p = {p_value:.4f}")

        # Bootstrap 95% CI
        ci = self._bootstrap_ci(df, n_bootstrap=1000)

        logger.info(f"95% CI: [{ci[0]:.3f}, {ci[1]:.3f}]")

        return rho, p_value, ci

    def fit_logistic_regression(
        self,
        df: pd.DataFrame
    ) -> Dict[str, Dict[str, float]]:
        """Secondary analysis: Logistic regression.

        Args:
            df: DataFrame with predictor and outcome columns

        Returns:
            Dictionary with odds ratios and confidence intervals
        """
        logger.info("Fitting logistic regression...")

        X = df[['env_file', 'pinned_deps', 'dockerfile', 'pub_year', 'log_model_params']]
        y = df['reproduced_within_12m']

        self.logistic_model.fit(X, y)

        # Compute odds ratios
        odds_ratios = np.exp(self.logistic_model.coef_[0])

        logger.info(f"Odds ratios: {dict(zip(X.columns, odds_ratios))}")

        # Compute confidence intervals via bootstrapping
        ci_results = self._bootstrap_logistic_ci(X, y, n_bootstrap=1000)

        return ci_results

    def _bootstrap_ci(
        self,
        df: pd.DataFrame,
        n_bootstrap: int = 1000,
        alpha: float = 0.05
    ) -> Tuple[float, float]:
        """Bootstrap confidence interval for Spearman correlation.

        Args:
            df: DataFrame with data
            n_bootstrap: Number of bootstrap iterations
            alpha: Significance level

        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        rhos = []
        n = len(df)

        for _ in range(n_bootstrap):
            indices = np.random.choice(n, size=n, replace=True)
            sample = df.iloc[indices]
            rho, _ = spearmanr(sample['doc_score'], sample['reproduced_within_12m'])
            rhos.append(rho)

        lower = np.percentile(rhos, alpha/2 * 100)
        upper = np.percentile(rhos, (1 - alpha/2) * 100)

        return (lower, upper)

    def _bootstrap_logistic_ci(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        n_bootstrap: int = 1000
    ) -> Dict:
        """Bootstrap confidence intervals for logistic regression coefficients.

        Args:
            X: Predictor DataFrame
            y: Outcome series
            n_bootstrap: Number of bootstrap iterations

        Returns:
            Dictionary with OR, CI, and p-value for each predictor
        """
        n = len(X)
        coef_samples = []

        for _ in range(n_bootstrap):
            indices = np.random.choice(n, size=n, replace=True)
            X_sample = X.iloc[indices]
            y_sample = y.iloc[indices]

            try:
                model = LogisticRegression(max_iter=1000, random_state=self.random_seed)
                model.fit(X_sample, y_sample)
                coef_samples.append(model.coef_[0])
            except Exception:
                continue

        coef_samples = np.array(coef_samples)

        results = {}
        for i, col in enumerate(X.columns):
            or_samples = np.exp(coef_samples[:, i])
            results[col] = {
                'OR': np.median(or_samples),
                'CI_lower': np.percentile(or_samples, 2.5),
                'CI_upper': np.percentile(or_samples, 97.5),
                'p': 0.05  # Placeholder
            }

        return results
