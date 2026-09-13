"""
Variance Group Analyzer
Compares confidence variance between successful vs timeout proofs for h-m1
"""

from typing import Tuple, Dict
import numpy as np
from scipy.stats import ttest_ind


class VarianceGroupAnalyzer:
    """Analyze confidence variance by outcome group (successful vs timeout)."""

    def separate_by_outcome(self, variances: np.ndarray, outcomes: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Separate variance values by outcome group.

        Args:
            variances: confidence variance values, shape [N]
            outcomes: binary outcomes (0=success, 1=timeout), shape [N]

        Returns:
            successful_variances: variances for successful proofs
            timeout_variances: variances for timeout proofs
        """
        successful_variances = variances[outcomes == 0]
        timeout_variances = variances[outcomes == 1]
        return successful_variances, timeout_variances

    def analyze_by_outcome(self, variances: np.ndarray, outcomes: np.ndarray) -> Dict:
        """
        Compute variance statistics for each outcome group.

        Args:
            variances: confidence variance values, shape [N]
            outcomes: binary outcomes (0=success, 1=timeout), shape [N]

        Returns:
            analysis: {
                'successful': {'count', 'mean_variance', 'std_variance'},
                'timeout': {'count', 'mean_variance', 'std_variance'},
                'difference': float (timeout - successful),
                't_statistic': float,
                'p_value': float
            }
        """
        successful_vars, timeout_vars = self.separate_by_outcome(variances, outcomes)

        # Compute statistics for each group
        successful_stats = {
            'count': len(successful_vars),
            'mean_variance': float(np.mean(successful_vars)) if len(successful_vars) > 0 else 0.0,
            'std_variance': float(np.std(successful_vars)) if len(successful_vars) > 0 else 0.0,
        }

        timeout_stats = {
            'count': len(timeout_vars),
            'mean_variance': float(np.mean(timeout_vars)) if len(timeout_vars) > 0 else 0.0,
            'std_variance': float(np.std(timeout_vars)) if len(timeout_vars) > 0 else 0.0,
        }

        # Compute difference
        difference = timeout_stats['mean_variance'] - successful_stats['mean_variance']

        # Statistical test (independent t-test)
        if len(successful_vars) > 1 and len(timeout_vars) > 1:
            t_stat, p_value = ttest_ind(timeout_vars, successful_vars)
        else:
            t_stat, p_value = 0.0, 1.0

        return {
            'successful': successful_stats,
            'timeout': timeout_stats,
            'difference': difference,
            't_statistic': float(t_stat),
            'p_value': float(p_value)
        }

    def evaluate_gate(self, analysis: Dict) -> bool:
        """
        Gate condition evaluation for h-m1.

        Args:
            analysis: output from analyze_by_outcome()

        Returns:
            True if gate passes (successful mean_variance < timeout mean_variance)
        """
        return analysis['successful']['mean_variance'] < analysis['timeout']['mean_variance']
