"""Correlation Analysis Module

Computes Spearman correlation and partial correlation with bootstrap CI.
"""

from typing import Dict, Tuple
import pandas as pd
import numpy as np
from scipy.stats import spearmanr
from pingouin import partial_corr


class CorrelationAnalyzer:
    """Analyzes correlation between community metrics and documentation quality."""

    def __init__(self, random_seed: int = 42):
        """Initialize correlation analyzer.

        Args:
            random_seed: Random seed for reproducibility
        """
        self.random_seed = random_seed
        np.random.seed(random_seed)

    def compute_spearman(
        self,
        x: pd.Series,
        y: pd.Series,
        one_tailed: bool = True
    ) -> Dict:
        """Compute Spearman rank correlation.

        Args:
            x: First variable (e.g., commits_per_month)
            y: Second variable (e.g., dcs_3_score)
            one_tailed: Use one-tailed test (H1: positive correlation)

        Returns:
            Dict with keys: rho, p_value, n
        """
        # Remove NaN pairs
        valid_mask = x.notna() & y.notna()
        x_clean = x[valid_mask]
        y_clean = y[valid_mask]

        # Compute Spearman correlation
        rho, p_value_two_tailed = spearmanr(x_clean, y_clean)

        # Convert to one-tailed if requested
        if one_tailed:
            # One-tailed p-value: p/2 if rho > 0, else 1 - p/2
            p_value = p_value_two_tailed / 2.0 if rho > 0 else 1.0 - (p_value_two_tailed / 2.0)
        else:
            p_value = p_value_two_tailed

        return {
            'rho': rho,
            'p_value': p_value,
            'n': len(x_clean),
            'test_type': 'one_tailed' if one_tailed else 'two_tailed'
        }

    def compute_partial_correlation(
        self,
        df: pd.DataFrame,
        x: str,
        y: str,
        covar: str
    ) -> Dict:
        """Compute partial correlation controlling for covariate.

        Args:
            df: DataFrame with all variables
            x: First variable name
            y: Second variable name
            covar: Covariate to control for (e.g., 'repo_age_days')

        Returns:
            Dict with keys: rho, p_value, n
        """
        # Remove rows with NaN in any of the three variables
        subset_cols = [x, y, covar]
        df_clean = df[subset_cols].dropna()

        # Compute partial correlation using pingouin
        result = partial_corr(data=df_clean, x=x, y=y, covar=covar, method='spearman')

        return {
            'rho': float(result['r'].iloc[0]),
            'p_value': float(result['p_val'].iloc[0]),  # pingouin uses 'p_val' with underscore
            'n': int(result['n'].iloc[0])
        }

    def bootstrap_confidence_interval(
        self,
        x: pd.Series,
        y: pd.Series,
        n_iterations: int = 10000,
        confidence_level: float = 0.95
    ) -> Tuple[float, float]:
        """Compute bootstrap confidence interval for Spearman correlation.

        Args:
            x: First variable
            y: Second variable
            n_iterations: Number of bootstrap iterations
            confidence_level: Confidence level (default 0.95 = 95%)

        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        # Remove NaN pairs
        valid_mask = x.notna() & y.notna()
        x_clean = x[valid_mask].values
        y_clean = y[valid_mask].values
        n = len(x_clean)

        # Bootstrap resampling
        boot_rhos = []
        for _ in range(n_iterations):
            # Resample with replacement
            indices = np.random.choice(n, size=n, replace=True)
            x_boot = x_clean[indices]
            y_boot = y_clean[indices]

            # Compute Spearman rho for this bootstrap sample
            try:
                rho_boot, _ = spearmanr(x_boot, y_boot)
                if not np.isnan(rho_boot):  # Skip NaN values (constant arrays)
                    boot_rhos.append(rho_boot)
            except:
                pass  # Skip failures

        # Compute percentile confidence interval
        if len(boot_rhos) == 0:
            # Fallback if all bootstrap samples failed
            return (np.nan, np.nan)

        alpha = 1.0 - confidence_level
        lower_percentile = (alpha / 2.0) * 100
        upper_percentile = (1.0 - alpha / 2.0) * 100

        ci_lower = np.percentile(boot_rhos, lower_percentile)
        ci_upper = np.percentile(boot_rhos, upper_percentile)

        return (float(ci_lower), float(ci_upper))

    def analyze_all_metrics(self, df: pd.DataFrame) -> Dict:
        """Analyze correlations for all activity metrics vs DCS_3.

        Args:
            df: DataFrame with columns [dcs_3_score, commits_per_month,
                                         unique_contributors, median_issue_response,
                                         repo_age_days]

        Returns:
            Dict with correlation results for each metric
        """
        results = {}

        activity_metrics = [
            ('commits_per_month', 'Commits/Month'),
            ('unique_contributors', 'Contributors'),
            ('median_issue_response', 'Issue Response Time')
        ]

        for metric_col, metric_label in activity_metrics:
            if metric_col not in df.columns:
                continue

            print(f"\nAnalyzing: {metric_label} vs DCS_3")

            # Spearman correlation (primary test)
            spearman_result = self.compute_spearman(
                df[metric_col],
                df['dcs_3_score'],
                one_tailed=True
            )
            print(f"  Spearman ρ = {spearman_result['rho']:.3f}, p = {spearman_result['p_value']:.4f} (n={spearman_result['n']})")

            # Partial correlation (controlling for age)
            if 'repo_age_days' in df.columns:
                partial_result = self.compute_partial_correlation(
                    df,
                    x=metric_col,
                    y='dcs_3_score',
                    covar='repo_age_days'
                )
                print(f"  Partial ρ = {partial_result['rho']:.3f}, p = {partial_result['p_value']:.4f} (age-controlled)")
            else:
                partial_result = None

            # Bootstrap CI (primary correlation)
            ci_lower, ci_upper = self.bootstrap_confidence_interval(
                df[metric_col],
                df['dcs_3_score'],
                n_iterations=10000
            )
            print(f"  95% CI = [{ci_lower:.3f}, {ci_upper:.3f}]")

            results[metric_col] = {
                'spearman': spearman_result,
                'partial': partial_result,
                'bootstrap_ci': (ci_lower, ci_upper)
            }

        return results
