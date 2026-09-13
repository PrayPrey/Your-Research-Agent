"""Statistical testing for stratified attention analysis."""
import numpy as np
import pandas as pd
from scipy.stats import ttest_ind


def run_statistical_test(dataset: pd.DataFrame) -> dict:
    """Two-sample t-test: simple > complex.

    Returns: {simple_mean, complex_mean, t_stat, p_value, delta, cohen_d, ci_95}
    """
    simple_concentrations = dataset[dataset['complexity'] == 'simple']['concentration'].values
    complex_concentrations = dataset[dataset['complexity'] == 'complex']['concentration'].values

    # t-test
    t_stat, p_value = ttest_ind(simple_concentrations, complex_concentrations, alternative='greater')

    # Effect size (Cohen's d)
    pooled_std = np.sqrt((simple_concentrations.var() + complex_concentrations.var()) / 2)
    cohen_d = (simple_concentrations.mean() - complex_concentrations.mean()) / pooled_std

    # Bootstrap CI
    def bootstrap_ci(arr, n_iter=1000):
        np.random.seed(42)
        means = [np.random.choice(arr, len(arr), replace=True).mean() for _ in range(n_iter)]
        return (np.percentile(means, 2.5), np.percentile(means, 97.5))

    return {
        "simple_mean": float(simple_concentrations.mean()),
        "complex_mean": float(complex_concentrations.mean()),
        "delta": float(simple_concentrations.mean() - complex_concentrations.mean()),
        "t_statistic": float(t_stat),
        "p_value": float(p_value),
        "cohen_d": float(cohen_d),
        "ci_95_simple": bootstrap_ci(simple_concentrations),
        "ci_95_complex": bootstrap_ci(complex_concentrations),
        "n_simple": len(simple_concentrations),
        "n_complex": len(complex_concentrations)
    }
